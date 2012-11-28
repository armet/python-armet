# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from flapjack.resources import field
from . import forms


class Poll(resources.Model):
    form = forms.Poll

    include = {
        'published_recently': field('published_recently'),
        'forty_two': field('forty_two'),
        'choices': field('choice_set')
    }

    def prepare_question(self, obj, value):
        return value.encode('base64')


class Choice(resources.Model):
    form = forms.Choice
