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

    def serialize(self, obj=None):
        # If we have nothing; serialize as an empty object.
        if obj is None:
            return ''

        try:
            # Attempt to serialize the incoming object using the URL encoder.
            return super(URLSerializer, self).serialize(urlencode(obj, True))

        except TypeError:
            # Raise up our hands; we cannot serialize this.
            raise ValueError
