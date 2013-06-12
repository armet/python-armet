# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from collections import OrderedDict
from .base import Deserializer
from armet import media_types


if six.PY3:
    from urllib.parse import parse_qsl

else:
    from urlparse import parse_qsl


class URLDeserializer(Deserializer):

    media_types = media_types.URL

    def deserialize(self, text, encoding='utf8'):
        # Ensure we don't attempt to deserialize nothing.
        if text is None:
            raise ValueError

        try:
            # Attempt to desserialize the URL using the
            # URL decoder.
            data = OrderedDict()
            for name, value in parse_qsl(text, keep_blank_values=True):
                name = name.decode(encoding)
                if name not in data:
                    data[name] = []
                data[name].append(value.decode(encoding))
            return data

        except AttributeError:
            # Something went wront internally; bad input.
            raise ValueError
