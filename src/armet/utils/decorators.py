# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import functools


class classproperty(object):
    """Declares a read-only `property` that acts on the class object.
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(cls)


class boundmethod(object):
    """
    Declares a method that can be invoked as both an instance method
    and a class method.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, obj, cls):
        self.obj = obj if obj else cls
        return self

    def __call__(self, *args, **kwargs):
        return self.method(self.obj, *args, **kwargs)


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
