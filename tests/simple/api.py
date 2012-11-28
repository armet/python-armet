# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from flapjack.resources import field, relation
from . import forms


class Choice(resources.Model):
    form = forms.Choice


class Poll(resources.Model):
    form = forms.Poll

    include = {
        'choices': field('choice_set')
    }

    relations = {
        'choices': relation(Choice, embed=False, local=True)
    }


class Poll2(Poll):
    include = {
        'forty_two': field('forty_two'),
    }

    exclude = ('booths',)

    relations = {
    }
