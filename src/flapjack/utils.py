# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import datetime
import collections
import six


class classproperty(object):
    """Declares a read-only `property` that acts on the class object.
    """

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(cls)


def memoize(obj):
    """Memoizes a function based on the id of its first argument."""
    from functools import wraps

    cache = obj.cache = {}

    @wraps(obj)
    def memoizer(*args, **kwargs):
        identifier = id(args[0])
        if identifier not in cache:
            value = obj(*args, **kwargs)
            cache[identifier] = value
            return value

        return cache[identifier]

    return memoizer


def config(path, default):
    """Retrieve a namespaced configuration option from django."""
    from django.conf import settings
    try:
        segment = settings.FLAPJACK
        for arg in path.split('.'):
            segment = segment[arg.upper()]

        return segment

    except AttributeError:
        return default

    except KeyError:
        return default


def config_fallback(test, *args):
    """Test passed value and if `None` use config with the remaining params."""
    return test if test is not None else config(*args)


def load(name):
    """Loads the python attribute represented by the fully qualified name."""
    parts = name.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def for_all(value, method, test=None):
    """
    Replace the item with `method(value)` if test passes (or no test). The item
    refers to either values of a dict, values of a list, a string, or a single
    value.
    """
    if isinstance(value, six.string_types) and (test is None or test(value)):
        value = method(value)

    elif isinstance(value, collections.Mapping):
        for key in value:
            if test is None or test(value[key]):
                value[key] = method(value[key])

    elif isinstance(value, collections.Sequence):
        values = ()
        for index, item in enumerate(value):
            values += (method(item) if test is None or test(item) else item),

        value = values

    elif test is None or test(value):
        value = method(value)

    return value
