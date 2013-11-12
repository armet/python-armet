# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import json
from collections import Iterable
from .base import Serializer
from armet import media_types


class JSONSerializer(Serializer):

    media_types = media_types.JSON

    @staticmethod
    def _default(obj):
        if isinstance(obj, Iterable):
            # This is an iterable but not recognizable as such
            # by the JSON serializer (eg. generator).
            return list(obj)

        # Raise up our hands; we cannot serialize this.
        raise ValueError('Unable to serialize {}'.format(obj))

    def __init__(self, *args, **kwargs):
        # Let the base class figure out things.
        super(JSONSerializer, self).__init__(*args, **kwargs)

        #! The configuration options that are passed to the
        #! JSON serializer.
        self.options = {
            'ensure_ascii': True,
            'separators': (',', ':',),
            'default': self._default
        }

    def serialize(self, obj=None):
        # If we have nothing; serialize as an empty object.
        if obj is None:
            obj = {}

        # Ensure it is atleast wrapped in an array.
        if isinstance(obj, six.string_types) or not isinstance(obj, Iterable):
            obj = [obj]

        # Serialize the resultant text.
        text = json.dumps(obj, **self.options)

        # Return us to the base to enclose it inside of a response object.
        return super(JSONSerializer, self).serialize(text)
