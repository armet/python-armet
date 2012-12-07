# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import http
from flapjack import resources
from flapjack.resources import field, relation
from . import models


class Choice(resources.Model):
    model = models.Choice

    include = {
        'question': field('poll__question')
    }


    relations = {
        'question': relation('polls.api.Poll'),
        'poll': relation('polls.api.Poll'),
    }


class Poll(resources.Model):
    model = models.Poll

    include = {
        'choices': field('choice_set')
    }
