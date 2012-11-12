# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from .base import BaseResource, Meta


class Meta(Meta):
    pass


class Resource(six.with_metaclass(Meta, BaseResource)):
    """
    Implements a resource using bindings from django's ORM layer to
    simplify and pre-define every operation with sane defaults.
    """

    #! The django model to bind to for the ORM layer to work.
    model = None

    @property
    def queryset(self):
        return self.model.objects.all()

    def read(self):
        if self.identifier is not None:
            return self.queryset.filter(pk=self.identifier)

        return self.queryset.all()
