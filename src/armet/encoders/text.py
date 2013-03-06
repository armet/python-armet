# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into plain text.

@note
    This is close but not quite the `text/plain` mimetype defined in HTML5.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import datetime
import six
import os
import magic
import collections
from collections import Mapping
import decimal
import fractions
from ..http import Response as HttpResponse
from urllib import quote_plus
from .. import transcoders
from . import Encoder, utils
from six.moves import cStringIO


class Encoder(transcoders.Text, Encoder):

    def _encode_mapping(self, stream, depth, obj):
        for index, key in enumerate(obj):
            if depth:
                # If we have depth we need to offset the value.
                stream.write('\t' * depth)

            # Then write the key (as we know we have a dict now).
            stream.write('{}: '.format(key))

            # Write the value
            self._encode_value(stream, depth + 1, obj[key])

            # Move on to the next one.
            stream.write('\n')

    def _encode_sequence(self, stream, depth, obj):
        for index, item in enumerate(obj):
            if depth:
                # We're not first; add a line.
                stream.write('\n')

            # Write the value
            self._encode_value(stream, depth, item)

    def _encode_value(self, stream, depth, obj):
        if obj is None:
            # We have nothing; and nothing in text is nothing.
            stream.write('')

        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            self._encode_value(stream, depth, obj.isoformat())

        elif isinstance(obj, six.string_types):
            # We have a string; simply return what we have.
            stream.write(obj.replace('\n', '\\n'))

        elif isinstance(obj, collections.Mapping):
            # Some kind of dictionary.
            self._encode_mapping(stream, depth, obj)

        elif isinstance(obj, collections.Sequence):
            # Some kind of sequence.
            self._encode_sequence(stream, depth, obj)

        elif isinstance(obj, six.integer_types):
            # Some kind of number.
            stream.write(str(obj))

        elif isinstance(obj, (float, fractions.Fraction, decimal.Decimal)):
            # Some kind of something.
            stream.write(str(obj))

        elif isinstance(obj, bool):
            # Boolean
            stream.write("true" if obj else "false")

        else:
            # We have no idea what we are..
            self._encode_value(stream, depth, utils.coerce_value(obj))

    def encode(self, obj=None):
        # Instantiate an in-memory stream.
        stream = cStringIO()

        # Initiate the encoding of object to the stream.
        self._encode_value(stream, 0, obj)

        # Retrieve the value of the stream and close it.
        text = stream.getvalue()
        stream.close()

        # Return the encoded text.
        return text
