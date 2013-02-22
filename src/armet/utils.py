# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility.
"""
from __future__ import print_function, unicode_literals, division
import six
import collections


class classproperty(object):
    """Declares a read-only `property` that acts on the class object.
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(cls)


def extend(collection, value):
      """Extends a collection with a value."""
      if isinstance(value, collections.Mapping):
          if collection is None:
              collection = {}
          collection.update(**value)

      elif isinstance(value, six.string_types):
          if collection is None:
              collection = []
          collection.append(value)

      elif isinstance(value, collections.Iterable):
          if collection is None:
              collection = []
          collection.extend(value)

      return collection
