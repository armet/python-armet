# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from .base import Resource, Meta


class Meta(Meta):

    def __new__(cls, name, bases, attrs):
        """
        """
        # construct the class object.
        obj = super(Meta, cls).__new__(cls, name, bases, attrs)

        # return the constructed object; wipe off the magic -- not really.
        return obj


class Resource(six.with_metaclass(Meta, Resource)):
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
