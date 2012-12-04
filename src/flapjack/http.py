# -*- coding: utf-8 -*-
"""
Describes the authentication protocols and generalizations used to
authenticate access to a resource endpoint.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django import http

# Normalize `http.client` and `httplib`
# TODO: We can remove this when the move to python 3 is done
from six.moves import http_client as client

try:
    # Attempt to get additional status codes (added in python 3.2)
    getattr(client, 'PRECONDITION_REQUIRED')
    getattr(client, 'TOO_MANY_REQUESTS')
    getattr(client, 'REQUEST_HEADER_FIELDS_TOO_LARGE')
    getattr(client, 'NETWORK_AUTHENTICATION_REQUIRED')

except AttributeError:
    # Don't have em; add them
    client.PRECONDITION_REQUIRED = 428
    client.TOO_MANY_REQUESTS = 429
    client.REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    client.NETWORK_AUTHENTICATION_REQUIRED = 511


class Response(http.HttpResponse, BaseException):
    """Extends django's `HttpResponse` to more closely follow `HTTP/1.1`.
    """

    def __init__(self, *args, **kwargs):
        # Delegate to django to set us up right.
        super(Response, self).__init__(*args, **kwargs)

        if not self.content:
            # No need to specify the default content-type if we don't
            # have a body.
            del self['Content-Type']

    @http.HttpResponse.content.setter
    def content(self, value):
        # Delegate to django to actually set our content
        super(Response, self)._set_content(value)

        if self.content:
            # Hop in and set our content-length automatically because it just
            # feels right
            self['Content-Length'] = len(bytes(self.content))
