# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.utils.unittest import TestCase
from armet.query import QueryList
from armet.query.constants import OPERATIONS
from armet import exceptions
from django.db.models import Q
from .models import Poll


class QueryTestCase(TestCase):
    """Testing the Query parser
    """

    def parse(self, querystring):
        """Simple convenience function to unwrap the array of parameters.
        """
        return QueryList(querystring)[0]

    def test_empty(self):
        """Test an empty query string
        """
        item = QueryList('')
        self.assertEqual(vars(item.as_q()), vars(Q()))

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
        item = self.parse('fruit=apples,oranges')

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
            self.assertEqual(item.django_direction, djangoified)
            self.assertEqual(item.value, [])

    def test_bogus(self):
        """Test some bogusy query strings.
        """
        queries = [
            'foo:bogus=bar',
            'foo:asc&;bar:desc',
            ':asc',
            ':desc=foo',
        ]
        for query in queries:
            print(query)
            self.assertRaises(exceptions.BadRequest, QueryList, query)

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
        q = '''the.rolling.stones.iregex.not:asc=sympathy,for,the,devil&\
guns.n.roses.istartswith.not:desc=paradise,city&queen:asc'''

        # Don't care about the other ones, as they're testing the &
        item = QueryList(q)[1]
        self.assertEqual(item.path, ['guns', 'n', 'roses'])
        self.assertEqual(item.operation, 'istartswith')
        self.assertTrue(item.negated)
        self.assertEqual(item.django_direction, '-')
        self.assertEqual(item.value, ['paradise', 'city'])

    def test_as_q(self):
        """Test the q object generation
        """
        # Q objects cannot be cleanly compared.  Additionally, the Q object
        # construction in armet generates a bunch of extra no-op Q objects
        # which django compiles away.  So these must be compared to the results
        manager = Poll.objects
        equality = {
            'question': Q(),
            'id=3': Q(id=3),
            'choice.id=230': Q(choice__id=230),
            'id=7,9': Q(id=7) | Q(id=9),
            'question.icontains=laugh&choice.choice_text!=Yes':
                Q(question__icontains='laugh') & ~Q(choice__choice_text='Yes'),
            # 'question:asc=bar': Q(question='bar'),
            'question.icontains=regardless':
                Q(question__icontains='regardless'),
        }
        for name, qobject in equality.iteritems():
            found = list(manager.filter(qobject))
            shouldbe = list(manager.filter(QueryList(name).as_q()))
            self.assertEqual(found, shouldbe)

    def test_as_order(self):
        params = {
            'thing.asf': None,
            'asdf.asc': None,
            'wrggr:desc': '-wrggr',
            'wjtra24g:asc': 'wjtra24g',
        }

        got = QueryList('&'.join(params.keys())).as_order()
        expected = [x for x in params.values() if x is not None]
        self.assertEqual(got, expected)
