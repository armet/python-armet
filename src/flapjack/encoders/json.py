# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into a JSON response.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections import Sequence
import datetime
import json
import six
from .. import transcoders
from . import Encoder


class _JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if (isinstance(obj, datetime.datetime)
                or isinstance(obj, datetime.time)
                or isinstance(obj, datetime.date)):
            # This is some kind of date/time -- encode using ISO format
            return obj.isoformat()

        # TODO: base-64 encode a file stream
        # TODO: use `vars(obj)` to send an object instance back through
        #       if we can't figure anything else out about it

        # Raise up our hands; we can not encode this
        return super(_JSONEncoder, self).default(obj)


class Encoder(transcoders.Json, Encoder):

    def encode(self, obj=None):
        # Ensure we have at least an iterable as valid JSON must at least
        # be an array and this library would return invalid JSON in that case
        if isinstance(obj, six.string_types) and not isinstance(obj, Sequence):
            obj = obj,

        # Encode and return the resultant text
        return json.dumps(obj,
            ensure_ascii=True,
            separators=(',', ':'),
            cls=_JSONEncoder)
