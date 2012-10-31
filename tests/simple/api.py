# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from . import models


class Poll(resources.Model):
    model = models.Poll
