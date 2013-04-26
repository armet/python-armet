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

    def deserialize(self, text=None):
        data = OrderedDict()
        for name, value in parse_qsl(text, keep_blank_values=True):
            if name not in data:
                data[name] = []
            data[name].append(value)
        return data
