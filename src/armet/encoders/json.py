# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
import json
import collections
from armet import transcoders
from .base import Encoder


class _TypeCoerableJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, collections.Iterable):
            # This is an iterable but not recognizable as such
            # by the JSON encoder.
            return list(obj)

        # Raise up our hands; we cannot encode this.
        return super(_TypeCoerableJSONEncoder, self).default(obj)


class Encoder(transcoders.Json, Encoder):

    def __init__(self, *args, **kwargs):
        # Let the base class figure out things.
        super(Encoder, self).__init__(*args, **kwargs)

        #! The configuration options that are passed to the
        #! JSON encoder.
        self.options = {
            'ensure_ascii': True,
            'separators': (',', ':',),
            'cls': _TypeCoerableJSONEncoder
        }

        pprint = self.params.get('pretty_print', '')
        if pprint == '1' or pprint.lower() == 'true':
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
        return super(Encoder, self).encode(json.dumps(obj, **self.options))
