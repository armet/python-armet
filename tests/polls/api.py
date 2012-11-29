# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from . import models


class Choice(resources.Model):
    model = models.Choice


class Poll(resources.Model):
    model = models.Poll
