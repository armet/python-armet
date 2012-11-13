# -*- coding: utf-8 -*-
"""
Describes the decoder protocols and generalizations used to decode text into a
an object suitable for consumption by python.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import abc
import six
from .. import transcoders


class Decoder(six.with_metaclass(abc.ABCMeta, transcoders.Transcoder)):

    @abc.abstractmethod
    def decode(self, request, fields=None):
        """
        Transforms the request into an acceptable object for consumption.

        @returns
            The python object suitable for consumption.
        """
        pass
