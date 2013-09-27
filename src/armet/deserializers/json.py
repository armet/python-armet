# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import json
from .base import Deserializer
from armet import media_types


class JSONDeserializer(Deserializer):

    media_types = media_types.JSON

    def deserialize(self, request=None, text=None, encoding='utf8'):

        if text is None:
            # Read in the text from the request.
            text = request.read()

        # Ensure the text is decoded.
        if isinstance(text, six.binary_type):
            text = text.decode(encoding)

        try:
            # Attempt to deserialize the text.
            return json.loads(text)

        except TypeError:
            # Failed; possibly null.
            raise ValueError
