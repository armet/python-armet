# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import ujson as json
from collections import Iterable, Sequence, Mapping
from .base import Serializer
from armet import media_types


class JSONSerializer(Serializer):

    media_types = media_types.JSON

    def serialize(self, obj=None):
        # If we have nothing; serialize as an empty object.
        if obj is None:
            return '{}'

        # Ensure generators are evaluated.
        if (isinstance(obj, Iterable)
                and not isinstance(obj, Sequence)
                and not isinstance(obj, Mapping)):
            obj = list(obj)

        # Ensure it is atleast wrapped in an array.
        if isinstance(obj, six.string_types) or not isinstance(obj, Iterable):
            obj = [obj]

        # Serialize the resultant text.
        text = json.dumps(obj, ensure_ascii=False)

        # Return us to the base to enclose it inside of a response object.
        return super(JSONSerializer, self).serialize(text)
