# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from importlib import import_module


class Relationship(object):
    """
    Track a relationship on a specific key of a target object.

    NOTE: The idea is to do eventual self-discovery of the resource argument.
    """

    def __init__(self, key, resource):
        self.key = key
        self._resource = resource
        self._resource_cls = None

    @property
    def resource(self):
        if not self._resource_cls:
            if isinstance(self._resource, six.string_types):
                parts = self._resource.split('.')
                mod = import_module('.'.join(parts[:-1]))
                self._resource_cls = getattr(mod, parts[-1])

            else:
                self._resource_cls = self._resource

        return self._resource_cls
