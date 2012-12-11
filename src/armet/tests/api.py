# -*- coding: utf-8 -*-
""" Defines a minimal resource API.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from armet import resources
from armet.resources import field, relation
from . import models


class Choice(resources.Model):
    model = models.Choice


class Poll(resources.Model):
    model = models.Poll
    relations = {
        'choices': relation(Choice)
    }
    include = {
        'choices': field('choice_set')
    }
