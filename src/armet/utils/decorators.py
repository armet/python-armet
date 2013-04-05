# -*- coding: utf-8 -*-
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
