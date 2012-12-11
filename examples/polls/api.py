# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from armet import http
from armet import resources
from armet.resources import field, relation
from . import models


class Choice(resources.Model):
    model = models.Choice

    # include = {
    #     'question': field('poll__question')
    # }

    # relations = {
    #     'question': relation('polls.api.Poll'),
    #     'poll': relation('polls.api.Poll'),
    # }

    include = {
        'complex': field()
    }

    def prepare_complex(self, obj, value=None):
        return complex(1, 2)


class Poll(resources.Model):
    model = models.Poll

    include = {
        'choices': field('choice_set')
    }

    # relations = {
    #     'choices': relation('polls.api.Choice', embed=True, local=True, path='choice_text'),
    # }
