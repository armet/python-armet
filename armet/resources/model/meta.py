# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ..managed import meta
from . import options
import six


# Mapping of the canonical resource for a model.
_canonical_resources = {}


class ModelResourceBase(meta.ManagedResourceBase):

    options = options.ModelResourceOptions

    connectors = ['http', 'model']

    _related_models_cache = None

    def __new__(cls, name, bases, attrs):
        # Construct the class object.
        self = super(ModelResourceBase, cls).__new__(cls, name, bases, attrs)

        if self.meta and not self.meta.abstract:
            # Add this to the canonical resource dictionary.
            _canonical_resources[self.meta.model] = self

        # Return the constructed class object.
        return self

    @property
    def _related_models(self):
        if not self._related_models_cache:
            if hasattr(self, 'relationships'):
                # Construct a mapping of all relationships and their models.
                self._related_models_cache = {}
                for key, relation in six.iteritems(self.relationships):
                    self._related_models_cache[
                        relation.resource.meta.model] = key

        return self._related_models_cache
