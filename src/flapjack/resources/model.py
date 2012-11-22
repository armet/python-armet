# -*- coding: utf-8 -*-
"""Implements the RESTful resource protocol for django ORM-backed models.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from . import base


class BaseModel(base.BaseResource):

    @classmethod
    def slug(cls, obj):
        return obj.pk

    def read(self):
        return self.model.objects.all().iterator()
