# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into a JSON response.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections import Iterable, Mapping
import datetime
import json
import six
from .. import transcoders
from . import Encoder


class _TypeAwareJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            return obj.isoformat()

        # TODO: base-64 encode a file stream

        if isinstance(obj, Iterable):
            # Since we can iterate but apparently can't encode -- make this
            # a list and send it back through the json encoder.
            return list(obj)

        try:
            # Last attempt; use `vars(obj)` to grab everything that doesn't
            # start with an underscore from the object.
            iterator = six.iteritems(vars(obj))
            return dict((n, v) for n, v in iterator if not n.startswith('_'))

        except AttributeError:
            # Apparently this is not an object.
            pass

        # Raise up our hands; we can not encode this.
        return super(_TypeAwareJSONEncoder, self).default(obj)


class Encoder(transcoders.Json, Encoder):

    def encode(self, obj=None):
        # Ensure we have at least an iterable as valid JSON must at least
        # be an array and this library would return invalid JSON in that case
        if isinstance(obj, six.string_types) or not isinstance(obj, Iterable):
            if not isinstance(obj, Mapping) and not hasattr(obj, '__dict__'):
                obj = obj,

        # Encode and return the resultant text
        return json.dumps(obj,
            ensure_ascii=True,
            separators=(',', ':'),
            cls=_TypeAwareJSONEncoder)
