# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import Deserializer
from armet import media_types


if six.PY3:
    from urllib.parse import parse_qsl

else:
    from urlparse import parse_qsl


class URLDeserializer(Deserializer):

    media_types = media_types.URL

    def deserialize(self, request=None, text=None, encoding='utf8'):

        if text is None:
            # Read in the text from the request.
            text = request.read()

        # Ensure we don't attempt to deserialize nothing.
        if text is None:
            raise ValueError

        try:
            # Attempt to desserialize the URL using the
            # URL decoder.
            data = {}
            for name, value in parse_qsl(text, keep_blank_values=True):
                # Ensure values are properly decoded if neccessary.
                if isinstance(value, six.binary_type):
                    value = value.decode(encoding)

                if isinstance(name, six.binary_type):
                    name = name.decode(encoding)

                # Initialize the array.
                if name not in data:
                    data[name] = []

                # Append the data value.
                data[name].append(value)

            return data

        except AttributeError:
            # Something went wront internally; bad input.
            raise ValueError
