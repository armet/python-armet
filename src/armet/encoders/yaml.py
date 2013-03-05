# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into a YAML response.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections import Iterable, Mapping
import datetime
import yaml
import six
from .. import transcoders
from . import Encoder, utils
import types
import collections
import decimal
import fractions


class Encoder(transcoders.Yaml, Encoder):

    def _encode_value(self, obj):
        if obj is None:
            # We have nothing; and nothing in text is nothing.
            return None

        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            return self._encode_value(obj.isoformat())

        if isinstance(obj, six.string_types):
            # We have a string; simply return what we have.
            return bytes(obj)

        if isinstance(obj, collections.Mapping):
            # Some kind of dictionary.
            return {bytes(key): self._encode_value(obj[key]) for key in obj}

        if isinstance(obj, collections.Sequence):
            # Some kind of sequence.
            return [self._encode_value(item) for item in obj]

        if isinstance(obj, six.integer_types):
            # Some kind of number.
            return bytes(obj)

        if isinstance(obj, (float, fractions.Fraction, decimal.Decimal)):
            # Some kind of something.
            return bytes(obj)

        if isinstance(obj, bool):
            # Boolean.
            return b"true" if obj else b"false"

        # We have no idea what we are..
        return self._encode_value(utils.coerce_value(obj))

    def encode(self, obj=None):
        # Return the encoded text.
        return yaml.dump(self._encode_value(obj), default_flow_style=True)
