# -*- coding: utf-8 -*-
""" Defines a minimal resource API.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from armet import resources
from armet.resources import attribute, relation
from . import models


class Choice(resources.Model):
    model = models.Choice

    include = {
        'complex': attribute()
    }

    def prepare_complex(self, obj, value=None):
        return complex(1, 2)


class Poll(resources.Model):
    model = models.Poll

    include = {
        'choices': attribute('choice_set'),
        'answers': attribute('choice_set')
    }

    relations = {
        'answers': relation(Choice, path='choice_text', embed=True)
    }


class BoothSomethignElseBlahBlah(resources.Model):
    model = models.Booth


class Cushion(resources.Model):
    model = models.Cushion

    include = {
        'poll': attribute('booth__poll')
    }

    relations = {
        'poll': relation(Poll)
    }
