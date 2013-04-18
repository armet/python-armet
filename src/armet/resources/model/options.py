# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.exceptions import ImproperlyConfigured
from ..managed import options


class ModelResourceOptions(options.ManagedResourceOptions):

    def __init__(self, meta, name, bases):
        # Initalize base resource options.
        super(ModelResourceOptions, self).__init__(meta, name, bases)

        #! Reference to the declarative model defined by
        #! the Object Relational Mapper (ORM).
        self.model = meta.get('model')
        if self.model is None:
            raise ImproperlyConfigured(
                'Model resources must be bound to a model.')
