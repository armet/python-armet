# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into a MessagePack
response.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from datetime import date, time, datetime
from .. import transcoders
from . import Encoder, utils
import msgpack


class Encoder(transcoders.MessagePack, Encoder):

    def _type_fallback(self, obj):
        if isinstance(obj, (datetime, time, date)):
            # This is some kind of date/time -- encode using ISO format.
            return obj.isoformat()

        # Coerce this thing.  If we can't then just return and let Messagepack
        # freak out.  Theoretically this shouldn't happen
        return utils.coerce_value(obj) or obj

    def encode(self, obj=None):
        # Return the encoded text.
        return msgpack.packb(obj, default=self._type_fallback)
