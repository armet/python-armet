# -*- coding: utf-8 -*-
"""
Describes the encoder protocols and generalizations used to
encode objects to a format suitable for transmission.
"""
from __future__ import absolute_import, unicode_literals, division
import abc
import six
import mimeparse


class Serializer(six.with_metaclass(abc.ABCMeta)):

    #! Applicable media types for this serializer.
    media_types = ()

    @classmethod
    def is_candidate(cls, media_ranges):
        """
        Determine if this serializer might be
        able to serialize appropriately.
        """
        try:
            # Attempt to use mimeparse to determine if the mimetype matches
            return mimeparse.best_match(cls.mimetypes, media_ranges) != ''

        except ValueError:
            # Mimeparse died something fierce (this happens when the
            # Accept header is in an invalid format).
            return False

    def __init__(self, accept, request, response):
        """
        @params[in] accept
            The accept header specifiying the media type.

        @params[in] response
            The http response class used to instantiate response objects.
        """
        # Parse out any parameters
        media_type = mimeparse.best_match(self.media_types, accept)
        self.params = mimeparse.parse_mime_type(media_type)[2]

        #! The request and response objects to use.
        self.request = request
        self.response = response

    def can_serialize(self, obj=None):
        """Tests this encoder to see if it can serialize the passed object."""
        try:
            # Attempt to serialize the object.
            self.serialize(obj)

            # The encoding process is assumed to have succeed.
            return True

        except ValueError:
            # The object was of an unsupported type.
            return False

    def serialize(self, data=None):
        """
        Transforms the object into an acceptable format for transmission.

        @throws ValueError
            To indicate this encoder does not support the encoding of the
            specified object.
        """
        if data is not None:
            # Set the content type.
            self.response['Content-Type'] = self.media_types[0]

            # Write the encoded and prepared data to the response.
            self.response.write(data)