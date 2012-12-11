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
from . import Encoder, utils


class _TypeAwareJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            return obj.isoformat()

        # Attempt to coerce this value.
        result = utils.coerce_value(obj)
        if result is not None:
            return result

        # Raise up our hands; we can not encode this.
        return super(_TypeAwareJSONEncoder, self).default(obj)


class Encoder(transcoders.Json, Encoder):

    def encode(self, obj=None):
        if obj is None:
            # If we have nothing; encode as an empty object.
            obj = {}

        # Encode and return the resultant text
        text = json.dumps(obj,
            ensure_ascii=True,
            separators=(',', ':'),
            cls=_TypeAwareJSONEncoder)

        # Ensure it is atleast wrapped in an array.
        if not (text.startswith('[') or text.startswith('{')):
            text = '[{}]'.format(text)

        # Return our encoded result
        return text
