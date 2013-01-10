# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.utils.unittest import TestCase
from armet.query import Query


class QueryTestCase(TestCase):
    """Testing the Query parser
    """

    def setUp(self):
        self.parser = Query()

    def tearDown(self):
        """ Delete the parser after every test to flush the parameters array
        """
        del self.parser

    def add(self, querystring):
        """Simple convenience function to add a query string and return
        the query object
        """
        self.parser.add_query(querystring)
        return self.parser.parameters[0]

    def test_simple_filter(self):
        query = self.add('foo=bar')
        self.assertEqual(query.path, ['foo'])
        self.assertEqual(query.operation, 'exact')
        self.assertFalse(query.negated)
        self.assertFalse(query.direction)
        self.assertEqual(query.value, ['bar'])

    def test_relational_filter(self):
        query = self.add('bread__sticks=delicious')

        self.assertEqual(query.path, ['bread', 'sticks'])
        self.assertEqual(query.operation, 'exact')
        self.assertFalse(query.negated)
        self.assertFalse(query.direction)
        self.assertEqual(query.value, ['delicious'])

    def test_negation(self):
        query = self.add('cheese__not=cheddar')

        self.assertEqual(query.path, ['cheese'])
        self.assertEqual(query.operation, 'exact')
        self.assertTrue(query.negated)
        self.assertFalse(query.direction)
        self.assertEqual(query.value, ['cheddar'])

    def test_multiple_values(self):
        query = self.add('fruit=apples;oranges')

        self.assertEqual(query.path, ['fruit'])
        self.assertEqual(query.operation, 'exact')
        self.assertFalse(query.negated)
        self.assertFalse(query.direction)
        self.assertEqual(query.value, ['apples', 'oranges'])

    def test_sorting(self):

        directions = {'aSc': '+', 'dEsC': '-'}

        for direction, djangoified in directions.iteritems():
            self.parser.add_query('marinas:{}=trench'.format(direction))
            query = self.parser.parameters[-1]

            self.assertEqual(query.path, ['marinas'])
            self.assertEqual(query.operation, 'exact')
            self.assertFalse(query.negated)
            self.assertEqual(query.direction, djangoified)
            self.assertEqual(query.value, ['trench'])

    def test_operations(self):
        operations = (
            'exact', 'iexact', 'contains', 'icontains', 'gt', 'gte', 'lt',
            'lte', 'in', 'startswith', 'istartswith', 'endswith', 'iendswith',
            'range', 'year', 'month', 'day', 'week_day', 'isnull', 'search',
            'regex', 'iregex',
        )
        for operation in operations:
            self.add('crazy__{}=true'.format(operation))
            query = self.parser.parameters[-1]
            self.assertEqual(query.path, ['crazy'])
            self.assertEqual(query.operation, operation)
            self.assertFalse(query.negated)
            self.assertFalse(query.direction)
            self.assertEqual(query.value, ['true'])

    def test_fusion(self):
        """Test something from everything combined
        """
        q = 'the__rolling__stones__iregex__not:asc=sympathy;for;the;devil'
        query = self.add(q)
        self.assertEqual(query.path, ['the', 'rolling', 'stones'])
        self.assertEqual(query.operation, 'iregex')
        self.assertTrue(query.negated)
        self.assertEqual(query.direction, '+')
        self.assertEqual(query.value, ['sympathy', 'for', 'the', 'devil'])
