# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
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
    """Memoizes a function based on its arguments."""
    from functools import wraps

    cache = obj.cache = {}

    @wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            value = obj(*args, **kwargs)
            cache[args] = value
            return value

        return cache[args]

    return memoizer


def config(path, default=None):
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
        return method(value)

    if isinstance(value, collections.Mapping):
        for key in value:
            if test is None or test(value[key]):
                value[key] = method(value[key])

        return value

    try:
        values = []
        for index, item in enumerate(value):
            values.append(method(item) if test is None or test(item) else item)

        return values

    except TypeError as ex:
        print(ex)
        pass

    if test is None or test(value):
        return method(value)

    return value

def fix_date(val):
   try:
       return val.isoformat()
   except AttributeError:
       return val
