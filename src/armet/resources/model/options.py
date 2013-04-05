# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from armet.exceptions import ImproperlyConfigured
from ..resource import options


class ModelResourceOptions(options.ResourceOptions):

    def __init__(self, meta, name, bases):
        # Initalize base resource options.
        super(ModelResourceOptions, self).__init__(meta, name, bases)

        #! Reference to the declarative model defined by
        #! the Object Relational Mapper (ORM).
        self.model = meta.get('model')
        if self.model is None:
            raise ImproperlyConfigured(
                'Model resources must be bound to a model.')
