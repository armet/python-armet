# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


class Deserializer(object):

    #! Applicable media types for this deserializer.
    media_types = ()

    def can_deserialize(self, text=None):
        """Tests this deserializer to see if it can deserialize."""
        try:
            # Attempt to deserialize the object.
            self.deserialize(text)

            # The deserialization process is assumed to have succeed.
            return True

        except ValueError:
            # The object was of an unsupported type.
            return False

    def deserialize(self, text=None):
        """Parses the text into a format consumable by python.

        @throws ValueError
            To indicate this deserializer cannot deserialize the
            passed text.
        """
        return text
