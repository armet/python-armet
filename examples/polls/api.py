# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from armet import http
from armet import resources
from armet.resources import attribute, relation
from . import models


class Choice(resources.Model):
    model = models.Choice

    # include = {
    #     'question': attribute('poll__question')
    # }

    # relations = {
    #     'question': relation('polls.api.Poll'),
    #     'poll': relation('polls.api.Poll'),
    # }

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
