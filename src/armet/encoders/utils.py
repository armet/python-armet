# -*- coding: utf-8 -*-
"""Declares small functions or classes of general utility for the encoders.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import datetime


def coerce_dict(obj):
    """Attempts to coerce the passed object as a dictionary."""
    try:
        # Last attempt; use `vars(obj)` to grab everything that doesn't
        # start with an underscore from the object.
        iterator = six.iteritems(vars(obj))
        return dict((n, v) for n, v in iterator if not n.startswith('_'))

    except (AttributeError, TypeError) as ex:
        # Apparently this is not an object.
        print(ex)
        pass

    # Attmept to go about vars(obj) a different way; here we use a
    # combination of `dir` and `__getattribute__` to strip off fields that
    # aren't class fields.
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
    if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
        # This is some kind of date/time -- encode using ISO format.
        return obj.isoformat()

        # TODO: base-64 encode a file stream

    if isinstance(obj, collections.Iterable):
        # Since we can iterate but apparently can't encode -- make this
        # a list and send it back through the json encoder.
        return list(obj)

    # Attempt to coerce this as a dictionary
    value = coerce_dict(obj)
    if value is not None:
        return value

    try:
        # Attempt to invoke the object.
        return obj()

    except TypeError:
        # Failed; move along
        pass

    # We have no idea; return nothing
