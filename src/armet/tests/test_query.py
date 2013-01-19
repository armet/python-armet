# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.utils.unittest import TestCase
from armet.query import parse, OPERATIONS
from armet import exceptions
from django.db.models import Q


class QueryTestCase(TestCase):
    """Testing the Query parser
    """

    def parse(self, querystring):
        """Simple convenience function to unwrap the array of parameters.
        """
        return parse(querystring)[0]

    def test_simple_filter(self):
        item = self.parse('foo=bar')
        self.assertEqual(item.path, ['foo'])
        self.assertEqual(item.operation, 'exact')
        self.assertFalse(item.negated)
        self.assertFalse(item.direction)
        self.assertEqual(item.value, ['bar'])

    def test_relational_filter(self):
        item = self.parse('bread.sticks=delicious')

        self.assertEqual(item.path, ['bread', 'sticks'])
        self.assertEqual(item.operation, 'exact')
        self.assertFalse(item.negated)
        self.assertFalse(item.direction)
        self.assertEqual(item.value, ['delicious'])

    def test_negation(self):
        item = self.parse('cheese.not=cheddar')

        self.assertEqual(item.path, ['cheese'])
        self.assertEqual(item.operation, 'exact')
        self.assertTrue(item.negated)
        self.assertFalse(item.direction)
        self.assertEqual(item.value, ['cheddar'])

    def test_multiple_values(self):
        item = self.parse('fruit=apples;oranges')

        self.assertEqual(item.path, ['fruit'])
        self.assertEqual(item.operation, 'exact')
        self.assertFalse(item.negated)
        self.assertFalse(item.direction)
        self.assertEqual(item.value, ['apples', 'oranges'])

    def test_sorting(self):

        directions = {'aSc': '', 'dEsC': '-'}

        for direction, djangoified in directions.iteritems():
            item = self.parse('marinas:{}'.format(direction))

            self.assertEqual(item.path, ['marinas'])
            self.assertEqual(item.operation, 'exact')
            self.assertFalse(item.negated)
            self.assertEqual(item.direction, djangoified)
            self.assertEqual(item.value, [])

    def test_bogus(self):
        queries = [
            'foo:bogus=bar'
            'foo=bogus=bar'
            'icontains.not=bar'
            ':asc'
            ':desc=foo'
        ]
        for query in queries:
            self.assertRaises(exceptions.BadRequest, parse, query)

    def test_operations(self):
        for operation in OPERATIONS:
            item = self.parse('crazy.{}=true'.format(operation))
            self.assertEqual(item.path, ['crazy'])
            self.assertEqual(item.operation, operation)
            self.assertFalse(item.negated)
            self.assertFalse(item.direction)
            self.assertEqual(item.value, ['true'])

    def test_fusion(self):
        """Test something from everything combined
        """
        q = '''the.rolling.stones.iregex.not:asc=sympathy;for;the;devil&\
guns.n.roses.istartswith.not:desc=paradise;city&queen:asc'''

        # Don't care about the other ones, as they're testing the &
        item = parse(q)[1]
        self.assertEqual(item.path, ['guns', 'n', 'roses'])
        self.assertEqual(item.operation, 'istartswith')
        self.assertTrue(item.negated)
        self.assertEqual(item.direction, '-')
        self.assertEqual(item.value, ['paradise', 'city'])

    def test_as_q(self):
        equality = {
            'amazing_q': Q(),
            'thing=foo': Q(thing__exact='foo'),
            'youre.a.kitty=yes': Q(youre__a__kitty__exact='yes'),
            'foo=bar;baz': Q(foo__exact='bar') | Q(foo__exact='baz'),
            'x=y&z=t': Q(x__exact='y') & Q(z__exact='t'),
            'sort:asc=bar': Q(sort__exact='bar'),
            'some.iexact=people': Q(some__iexact='people'),
        }
        for name, qobject in equality.iteritems():
            # Q objects don't have an equality operator, so compare their vars
            self.assertEqual(vars(parse(name).as_q()), vars(qobject))

    def test_as_order(self):
        params = {
            'thing.asf': None,
            'asdf.asc': None,
            'wrggr:desc': '-wrggr',
            'wjtra24g:asc': 'wjtra24g',
        }

        got = parse('&'.join(params.keys())).as_order()
        expected = [x for x in params.values() if x is not None]
        self.assertEqual(got, expected)
