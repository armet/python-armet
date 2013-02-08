# -*- coding: utf-8 -*-
"""Implements the decoder protocol for `XML` objects.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from lxml import objectify
from .. import transcoders
from . import Decoder, DecoderError


## Leaving this here for now
# xml = '''
# <dataset>
#   <statusthing>success</statusthing>
#   <datathing gabble="sent">joe@email.com</datathing>
#   <datathing gabble="not sent"></datathing>
# </dataset>
# '''


# root = objectify.fromstring(xml)

# print vars(root)


class Decoder(transcoders.XML, Decoder):

    def decode(self, request, attributes=None):
        try:
            # Attempt to decode as a XML object

            return vars(objectify.fromstring(request.body))

        except ValueError:
            # Something unexpected; no XML could be decoded
            raise DecoderError()
