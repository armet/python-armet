# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
import six
import json
import collections
from armet import transcoders
from .base import Encoder


class _TypeCoerableJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        # Raise up our hands; we cannot encode this.
        return super(_TypeCoerableJSONEncoder, self).default(obj)


class Encoder(Encoder, transcoders.Json):

    def __init__(self, pretty_print=False):
        #! The configuration options that are passed to the
        #! JSON encoder.
        self.options = {
            'ensure_ascii': True,
            'separators': (',', ':',),
            'cls': _TypeCoerableJSONEncoder
        }

        if pretty_print:
            # We are pretty printing; turn on indents and
            # add spaces around separators
            self.options['indent'] = 2
            self.options['separators'] = (', ', ': ')

    def encode(self, obj=None):
        # If we have nothing; encode as an empty object.
        if obj is None:
            return '{}'

        # Ensure it is atleast wrapped in an array.
        if isinstance(obj, six.string_types):
            obj = [obj]

        elif not isinstance(obj, collections.Iterable):
            obj = [obj]

        # Encode and return the resultant text.
        return json.dumps(obj, **self.options)
