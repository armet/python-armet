# -*- coding: utf-8 -*-
"""Implements the decoder protocol for `multipart/form-data`.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from StringIO import StringIO
from django.http.multipartparser import MultiPartParser, MultiPartParserError
from .. import transcoders
from . import Decoder, DecoderError


class Decoder(transcoders.Form, Decoder):

    def decode(self, request, attributes=None):
        # Instantiate an instance of django's multi-part parser
        stream = StringIO(request.body)

        try:
            # Attempt to instantiate and parse the request using the built-in
            # django multi-part parser
            headers = request.META
            parser = MultiPartParser(headers, stream, request.upload_handlers)
            data, files = parser.parse()

        except MultiPartParserError:
            # Something went wrong here;
            raise DecoderError

        # Flatten the data dictionary if possible.
        obj = dict(data)

        # Merge files dictionary with the data dictionary.
        obj.update(dict(files))

        for key in obj:
            if attributes and key in attributes and attributes[key].collection:
                # Field declared to be an array; don't bother.
                continue

            if len(obj[key]) == 1:
                # Field probably supposed to be scalar.
                obj[key] = obj[key][0]

        # Return the decoded object.
        return obj
