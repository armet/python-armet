# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
from . import base


class Meta(base.Meta):

    @property
    def _form_fields(self):
        return self.form.declared_fields

    def _discover_fields(self):
        # Let the base class discover fields explicitly declared
        # on the form
        super(Meta, self)._discover_fields()


class Resource(six.with_metaclass(Meta, base.BaseResource)):
    """
    Implements a resource using bindings from django's ORM layer to
    simplify and pre-define every operation with sane defaults.
    """

    #! The django model to bind to for the ORM layer to work.
    model = None

    @property
    def queryset(self):
        return self.model.objects

    def read(self):
        if self.identifier is not None:
            return self.queryset.filter(pk=self.identifier)

        return self.queryset.all()
