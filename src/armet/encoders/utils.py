# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility for the encoders.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import six
import decimal


def coerce_dict(obj):
    """Attempts to coerce the passed object as a dictionary."""
    try:
        # Last attempt; use `vars(obj)` to grab everything that doesn't
        # start with an underscore from the object.
        iterator = six.iteritems(vars(obj))
        return dict((n, v) for n, v in iterator if not n.startswith('_'))

    except (AttributeError, TypeError):
        # Apparently this is not an object.
        pass

    # Attmept to go about vars(obj) a different way; here we use a
    # combination of `dir` and `__getattribute__` to strip off attributes that
    # aren't class attributes.
    try:
        result = {}
        for name in dir(obj):
            if not name.startswith('_'):
                try:
                    value = obj.__getattribute__(name)
                    if value != obj.__class__.__dict__[name]:
                        result[name] = obj.__getattribute__(name)

                except KeyError:
                    pass

        return result

    except AttributeError:
        # Guess that didn't work either.
        pass


def coerce_value(obj):
    try:
        # Attempt to encode a file as base64.
        return obj.read().encode('base64')

    except AttributeError:
        # Not a file; move along
        pass

    try:
        if isinstance(obj, complex):
            # Complex type; return it as a str
            return '{:G}+{:G}i'.format(obj.real, obj.imag)

    except NameError:
        # No complex type support here.
        pass

    if isinstance(obj, collections.Iterable):
        # Since we can iterate but apparently can't encode -- make this
        # a list and send it back through the json encoder.
        return list(obj)

    if isinstance(obj, decimal.Decimal):
        # Also check to see if this is a decimal, and return a string version
        return str(obj)

    try:
        # Attempt to invoke the object only if we're not a type.
        if not isinstance(obj, type):
            return obj()

    except TypeError:
        # Failed; move along
        pass

    # Attempt to coerce this as a dictionary
    value = coerce_dict(obj)
    if value is not None:
        return value

    # We have no idea; return nothing
