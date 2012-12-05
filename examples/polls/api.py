# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from flapjack.resources import field, relation
from . import models


class Choice(resources.Model):
    model = models.Choice

    # exclude = (
    #     'poll',
    # )


class Poll(resources.Model):
    model = models.Poll

    include = {
        'choices': field('choice_set')
    }

    relations = {
        'choices': relation(Choice, embed=False, local=True)
    }
