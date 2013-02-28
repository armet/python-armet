# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility.
"""
from __future__ import print_function, unicode_literals, division
import six
import re
import collections
import os
import pkgutil


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

    else:
        if collection is None:
            collection = []
        collection.append(value)

    return collection


def dasherize(value):
    """Dasherizes the passed value."""
    value = value.strip()
    value = re.sub(r'([A-Z])', r'-\1', value)
    value = re.sub(r'[-_\s]+', r'-', value)
    value = re.sub(r'^-', r'', value)
    value = value.lower()
    return value


def iter_modules(package):
    """Iterate through all modules of a packge."""
    mname = package.__name__
    modules = pkgutil.iter_modules([os.path.dirname(package.__file__)])
    for imp, name, _ in modules:
        yield imp.find_module(name).load_module('{}.{}'.format(mname, name))
