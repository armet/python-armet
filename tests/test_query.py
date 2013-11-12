# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
from armet.query import parser, constants
from pytest import mark


@mark.bench('parser.parse', iterations=10000)
class QueryTestCase(unittest.TestCase):

    def parse(self, text):
        """Simple convenience function to unwrap the array of parameters."""
        return parser.parse(text)

    def test_empty(self):
        """Test an empty query string."""
        item = self.parse('')

        assert len(item.segments) == 0

    def test_simple_filter(self):
        item = self.parse('foo=bar').segments[0]

        assert item.path == ['foo']
        assert item.operator, constants.OPERATOR_IEQUAL[0]
        assert not item.negated
        assert item.values == ['bar']

    def test_binary(self):
        item = self.parse(b'foo=bar').segments[0]

        assert item.path == ['foo']
        assert item.values == ['bar']

    def test_negation(self):
        queries = ['foo!=bar', 'foo.not=bar']
        for query in queries:
            item = self.parse(query).segments[0]

            assert item.negated

    def test_relational_filter(self):
        item = self.parse('bread.sticks=delicious').segments[0]

        assert item.path == ['bread', 'sticks']
        assert item.operator, constants.OPERATOR_IEQUAL[0]
        assert not item.negated
        assert item.values == ['delicious']

    def test_values(self):
        item = self.parse('fruit=apples,oranges').segments[0]

        assert item.path == ['fruit']
        assert item.operator, constants.OPERATOR_IEQUAL[0]
        assert not item.negated
        assert item.values == ['apples', 'oranges']

    def test_bogus(self):
        """Test some bogusy query strings."""
        queries = [
            'foo:asc&;bar:desc',
            'foo.lte<=3',
            'foo.!negate',
            'foo.negate=!3',
            'lte=3',
        ]
        for query in queries:
            self.assertRaises(ValueError, self.parse, query)

    def test_operations(self):
        for name, symbol in constants.OPERATORS:
            item = self.parse('crazy.{}=true'.format(name)).segments[0]

            assert item.path == ['crazy']
            assert item.operator == name
            assert not item.negated
            assert item.values == ['true']

            if symbol is not None:
                item = self.parse('crazy{}true'.format(symbol)).segments[0]

                assert item.path == ['crazy']
                assert item.operator == name
                assert not item.negated
                assert item.values == ['true']

    def test_fusion(self):
        """Test something from everything combined"""
        q = ('the.rolling.stones.iregex.not:asc=sympathy,for,the,devil&'
             '!guns.n.roses=paradise,city&queen:asc')

        # Don't care about the other ones, as they're testing the &
        item = self.parse(q).segments[1]

        assert item.path == ['guns', 'n', 'roses']
        assert item.operator == constants.OPERATOR_IEQUAL[0]
        assert item.negated
        assert item.values == ['paradise', 'city']
