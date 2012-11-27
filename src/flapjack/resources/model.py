# -*- coding: utf-8 -*-
"""Implements the RESTful resource protocol for django ORM-backed models.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from . import base


class BaseModel(base.BaseResource):

    #! The model this resource is bound to; shortcut for declaring a form
    #! for read-only resources.
    model = None

    @classmethod
    def slug(cls, obj):
        return obj.pk

    def read(self):
        # return self.model.objects.all().prefetch_related('choice_set')
        # return self.model.objects.all().prefetch_related('poll')
        return self.model.objects.all()
