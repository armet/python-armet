# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.utils.unittest import TestCase
from armet.query import parse, OPERATIONS
from armet import exceptions


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
        item = self.parse('bread__sticks=delicious')

        self.assertEqual(item.path, ['bread', 'sticks'])
        self.assertEqual(item.operation, 'exact')
        self.assertFalse(item.negated)
        self.assertFalse(item.direction)
        self.assertEqual(item.value, ['delicious'])

    def test_negation(self):
        item = self.parse('cheese__not=cheddar')

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

        directions = {'aSc': '+', 'dEsC': '-'}

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
            'icontains__not=bar'
        ]
        for query in queries:
            self.assertRaises(exceptions.BadRequest, parse, query)

    def test_operations(self):
        for operation in OPERATIONS:
            item = self.parse('crazy__{}=true'.format(operation))
            self.assertEqual(item.path, ['crazy'])
            self.assertEqual(item.operation, operation)
            self.assertFalse(item.negated)
            self.assertFalse(item.direction)
            self.assertEqual(item.value, ['true'])

    def test_fusion(self):
        """Test something from everything combined
        """
        q = '''the__rolling__stones__iregex__not:asc=sympathy;for;the;devil&\
guns__n__roses__istartswith__not:desc=paradise;city&queen:asc'''

        # Don't care about the other ones, as they're testing the &
        item = parse(q)[1]
        self.assertEqual(item.path, ['guns', 'n', 'roses'])
        self.assertEqual(item.operation, 'istartswith')
        self.assertTrue(item.negated)
        self.assertEqual(item.direction, '-')
        self.assertEqual(item.value, ['paradise', 'city'])
