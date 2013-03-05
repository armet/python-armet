# -*- coding: utf-8 -*-
""" Defines a minimal resource API.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from armet import resources, authentication, authorization
from armet.resources import attribute, relation
from . import models


class Poll(resources.Model):
    model = models.Poll
    authentication = (authentication.Basic(),)
    authorization = authorization.ModelAuthorization()
