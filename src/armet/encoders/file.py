# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object directly.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
# from datetime import date, time, datetime
from .. import transcoders, http
from . import Encoder, utils
import msgpack
import magic


class Encoder(transcoders.Direct, Encoder):

    def encode(self, obj=None):
        response = http.Response()
        try:
            response.content = obj.read()
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(obj.name.split('/')[-1])
            response['Content-Type'] = magic.from_buffer(response.content)
        except AttributeError:
            response.content = obj.read()
            response['Content-Disposition'] = 'attachment'
        return response
