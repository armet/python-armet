# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from .base import Serializer
from armet import media_types

# Import urlencode
if six.PY3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode


class URLSerializer(Serializer):

    media_types = media_types.URL

    def __init__(self, *args, **kwargs):
        super(URLSerializer, self).__init__(*args, **kwargs)

        # Passed to urlencode.  This causes array values to automatically be
        # expanded properly instead of causing crazy nested percent encoding.
        self.doseq = kwargs.get('doseq', True)

    def serialize(self, obj=None):

        if obj is None:
            obj = {}

        try:
            super(URLSerializer, self).serialize(urlencode(obj, self.doseq))

        except TypeError:
            raise ValueError
