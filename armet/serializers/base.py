# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division


class Serializer(object):

    #! Applicable media types for this serializer.
    media_types = ()

    def __init__(self, request=None, response=None):
        #! The request and response objects to use.
        self.request = request
        self.response = response

    def can_serialize(self, data=None):
        """Tests this serializer to see if it can serialize."""
        try:
            # Attet to serialize the object.
            self.serialize(data)

            # The serialization process is assumed to have succeed.
            return True

        except ValueError:
            # The object was of an unsupported type.
            return False

    def serialize(self, data=None):
        """
        Transforms the object into an acceptable format for transmission.

        @throws ValueError
            To indicate this serializer does not support the encoding of the
            specified object.
        """
        if data is not None and self.response is not None:
            # Set the content type.
            self.response['Content-Type'] = self.media_types[0]

            # Write the encoded and prepared data to the response.
            self.response.write(data)

        # Return the serialized data.
        # This has normally been transformed by a base class.
        return data
