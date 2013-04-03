# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility.
"""
from __future__ import print_function, unicode_literals, division
import six
import re
import collections
import os
import pkgutil
import importlib
import functools


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
    prefix = package.__name__
    path = os.path.dirname(package.__file__)
    for _, name, _ in pkgutil.iter_modules([path]):
        yield importlib.import_module('{}.{}'.format(prefix, name))


def memoize_single(function):
    """Memoization decorator for a function taking a single argument.

    @note
        This is roughly ~6 times faster than `memoize` under CPython 2.7.
    """
    class memoizer(dict):
        def __missing__(self, key):
            result = self[key] = function(key)
            return result
    return memoizer().__getitem__


class memoize(dict):
    """Memoization decorator for functions taking one or more arguments."""

    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # Uncacheable; just return.
            return self.function(*args)
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.function(*key)
        return result

    def __get__(self, obj, cls):
        return functools.partial(self.__call__, obj)
