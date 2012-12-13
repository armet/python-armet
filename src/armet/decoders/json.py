# -*- coding: utf-8 -*-
"""Implements the decoder protocol for `multipart/form-data`.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import json
from .. import transcoders
from . import Decoder, DecoderError


class Decoder(transcoders.Json, Decoder):

    def decode(self, request, attributes=None):
        try:
            # Attempt to decode as a JSON object
            return json.loads(request.body)

        except ValueError:
            # Something unexpected; no JSON could be decoded
            raise DecoderError()
