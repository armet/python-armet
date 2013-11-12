# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


class Deserializer(object):

    #! Applicable media types for this deserializer.
    media_types = ()

    def deserialize(self, request=None, text=None):
        """Parses the request content into a format consumable by python.

        @throws ValueError
            To indicate this deserializer cannot deserialize the
            passed text.
        """

        if text is None:
            # Read in the text from the request.
            text = request.read()

        return text
