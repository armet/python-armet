# -*- coding: utf-8 -*-
"""
Describes the encoder protocols and generalizations used to
encode objects to a format suitable for transmission.
"""
from __future__ import print_function, unicode_literals, division
import abc
import six
from armet import transcoders


class Encoder(six.with_metaclass(abc.ABCMeta, transcoders.Transcoder)):

    def __init__(self, response):
        """
        @params[in] response
            The http response class used to instantiate response objects.
        """
        self.response = response

    def can_encode(self, obj=None):
        """Tests this encoder to see if it can encode the passed object.
        """
        try:
            # Attempt to encode the object.
            self.encode(obj)

            # The encoding process is assumed to have succeed.
            return True

        except ValueError:
            # The object was of an unsupported type.
            return False

    @abc.abstractmethod
    def encode(self, obj=None):
        """
        Transforms the object into an acceptable format for transmission.

        @returns
            An http response object that can be directly returned to the
            client or just the content.

        @throws ValueError
            To indicate this encoder does not support the encoding of the
            specified object.
        """
