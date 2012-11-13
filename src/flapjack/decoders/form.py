# -*- coding: utf-8 -*-
"""Implements the decoder protocol for `multipart/form-data`.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from StringIO import StringIO
from django.http import MultiPartParser
from .. import transcoders
from . import Decoder


class Decoder(transcoders.Form, Decoder):

    def decode(self, request, fields=None):
        # Instantiate an instance of django's multi-part parser
        stream = StringIO(request.body)
        parser = MultiPartParser(request.META, stream, (), request.encoding)

        # Parse the form-data as data, files
        data, files = parser.parse()

        # Append values in files into the data dictionary
        obj = dict(data)
        for name in files:
            if name not in obj:
                obj[name] = []

            # This is absurd. Why can't we just do `files[name]` here.
            obj[name].extend(files.getlist([name]))

        # Normalize and flatten this as much as we can.
        for name in obj:
            if fields is None or name not in fields:
                # Field not declared; don't bother with it
                continue

            if fields[name].collection and len(obj[name]) == 1:
                # Field is really meant to be scalar
                obj[name] = obj[name][0]

        # Return the constructed object
        return obj
