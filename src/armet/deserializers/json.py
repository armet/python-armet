# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from .base import Deserializer
from armet import media_types


class JSONDeserializer(Deserializer):

    media_types = media_types.JSON

    def deserialize(self, text=None):
        try:
            # Attempt to deserialize the text.
            return json.loads(text)

        except TypeError:
            # Failed; possibly null.
            raise ValueError
