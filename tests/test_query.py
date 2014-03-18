# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
import six
from armet.query import parser, constants
from pytest import mark


@mark.bench('parser.parse', iterations=10000)
class QueryTestCase(unittest.TestCase):

    def parse(self, text):
        """Simple convenience function to unwrap the array of parameters."""
        return parser.parse(text).parsed

    def test_empty(self):
        """Test an empty query string."""
        item = self.parse('')

        assert isinstance(item, parser.NoopQuerySegment)

    def test_simple_filter(self):
        item = self.parse('foo=bar')

        assert item.path == ['foo']
        assert item.operator, constants.OPERATOR_IEQUAL[0]
        assert not item.negated
        assert item.values == ['bar']

    def test_binary(self):
        item = self.parse(b'foo=bar')

        assert item.path == ['foo']
        assert item.values == ['bar']

    def test_negation(self):
        queries = ['foo!=bar', 'foo.not=bar']
        for query in queries:
            item = self.parse(query)

            assert item.negated

    def test_relational_filter(self):
        item = self.parse('bread.sticks=delicious')

        assert item.path == ['bread', 'sticks']
        assert item.operator, constants.OPERATOR_IEQUAL[0]
        assert not item.negated
        assert item.values == ['delicious']

    def test_values(self):
        item = self.parse('fruit=apples,oranges')

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
            'lte=3',
        ]
        for query in queries:
            self.assertRaises(ValueError, self.parse, query)

    def test_operations(self):
        for name, symbol in constants.OPERATORS:
            item = self.parse('crazy.{}=true'.format(name))

            assert item.path == ['crazy']
            assert item.operator == constants.OPERATOR_SUFFIX_MAP[name]
            assert not item.negated
            assert item.values == ['true']

            if symbol is not None:
                item = self.parse('crazy{}true'.format(symbol))

                assert item.path == ['crazy']
                assert item.operator == constants.OPERATOR_EQUALITY_MAP[symbol]
                assert not item.negated
                assert item.values == ['true']

    def test_fusion(self):
        """Test something from everything combined"""
        q = ('the.rolling.stones.iregex.not:asc=sympathy,for,the,devil;'
             '!(guns.n.roses=paradise,city&queen:asc)')

        item = self.parse(q)

        # I'm lazy and don't want to walk the tree, so lets just test the repr.
        assert (six.text_type(repr(item)) ==
                "(the.rolling.stones.iregex.not:asc :iexact 'sympathy' "
                "| 'for' | 'the' | 'devil') OR NOT (guns.n.roses :iexact "
                "'paradise' | 'city') AND (queen :iexact '')")

    def test_grouping(self):
        item = self.parse('foo=bar&(a=b;b=c)')

        assert item.left.path == ['foo']
        assert item.right.left.path == ['a']
        assert item.right.right.path == ['b']
