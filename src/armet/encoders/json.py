# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import six
import json
from collections import Iterable
from armet import transcoders
from .base import Encoder


class TypeCoerableJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Iterable):
            # This is an iterable but not recognizable as such
            # by the JSON encoder (eg. generator).
            return list(obj)

        # Raise up our hands; we cannot encode this.
        raise ValueError('Unable to encode {}'.format(obj))


class Encoder(transcoders.Json, Encoder):

    def __init__(self, *args, **kwargs):
        # Let the base class figure out things.
        super(Encoder, self).__init__(*args, **kwargs)

        #! The configuration options that are passed to the
        #! JSON encoder.
        self.options = {
            'ensure_ascii': True,
            'separators': (',', ':',),
            'cls': TypeCoerableJSONEncoder
        }

    def encode(self, obj=None):
        # If we have nothing; encode as an empty object.
        if obj is None:
            obj = {}

        # Ensure it is atleast wrapped in an array.
        if isinstance(obj, six.string_types) or not isinstance(obj, Iterable):
            obj = [obj]

        # Encode the resultant text.
        super(Encoder, self).encode(json.dumps(obj, **self.options))
