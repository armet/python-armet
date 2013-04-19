# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import collections


def cons(collection, value):
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

    else:
        if collection is None:
            collection = []
        collection.append(value)

    return collection
