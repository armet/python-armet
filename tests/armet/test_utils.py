# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import utils
from pytest import mark


@mark.bench('utils.cons', number=1000000)
class TestConstruction:

    def test_mapping(self):
        lhs = {'x': 10, 'y': 20}
        rhs = {'z': 15}

        value = utils.cons(lhs, rhs)

        assert value == {'x': 10, 'y': 20, 'z': 15}

    def test_list(self):
        lhs = [10, 20]
        rhs = [15]

        value = utils.cons(lhs, rhs)

        assert value == [10, 20, 15]

    def test_scalar(self):
        lhs = [10, 20]
        rhs = 15

        value = utils.cons(lhs, rhs)

        assert value == [10, 20, 15]

    def test_string(self):
        lhs = ['10', 20]
        rhs = '15'

        value = utils.cons(lhs, rhs)

        assert value == ['10', 20, '15']


@mark.bench('utils.dasherize', number=1000000)
class TestDasherize:

    def test_word(self):
        assert utils.dasherize('word') == 'word'

    def test_camel(self):
        assert utils.dasherize('camelCase') == 'camel-case'

    def test_pascal(self):
        assert utils.dasherize('PascalCase') == 'pascal-case'

    def test_underscore(self):
        assert utils.dasherize('under_score') == 'under-score'

    def test_dashed(self):
        assert utils.dasherize('dashed-words') == 'dashed-words'
