# -*- coding: utf-8 -*-
"""
Describes the encoder protocols and generalizations used to
encode objects to a format suitable for transmission.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
import six
from .. import transcoders


class Encoder(six.with_metaclass(abc.ABCMeta, transcoders.Transcoder)):

    @abc.abstractmethod
    def encode(self, obj=None):
        """
        Transforms objects into an acceptable format for tansmission.

        @returns
            A string containing all neccessary information
            that can be provided.
        """
        pass
