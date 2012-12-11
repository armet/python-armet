# -*- coding: utf-8 -*-
"""Implements the decoder protocol for `multipart/form-data`.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from StringIO import StringIO
from django.http import MultiPartParser
from .. import transcoders
from . import Decoder
from django.core.files.uploadhandler import load_handler


class Decoder(transcoders.Form, Decoder):

    def decode(self, request, fields=None):
        # Instantiate an instance of django's multi-part parser
        stream = StringIO(request.body)
        handlers =[ load_handler('django.core.files.uploadhandler.TemporaryFileUploadHandler', request) ]
        parser = MultiPartParser(request.META, stream, handlers, request.encoding)

        # Parse the form-data as data, files
        data, files = parser.parse()

        data = dict(data)

        #flatten the data dictionary if possible
        for key in data:
            if (len(data[key]) == 1):
                data[key] = data[key][0]

        data.update(dict(files))
        return data

"""        # Append values in files into the data dictionary
        obj = dict(data)
        for name in files:
            if name not in obj:
                obj[name] = []

            # This is absurd. Why can't we just do `files[name]` here?
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
        return obj """
