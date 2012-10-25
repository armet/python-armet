# coding=utf-8
""" ..
"""
from django import http


#! Bad request [RFC 2616 § 10.4.1]
#! The request could not be understood by the server due to malformed syntax.
BAD_REQUEST = 400


#! Not found [RFC 2616 §10.4.5]
NOT_FOUND = 404


class HttpResponse(http.HttpResponse):
    """Extends django's `HttpResponse` to more closely follow `HTTP/1.1`.
    """

    def __init__(self, *args, **kwargs):
        super(HttpResponse, self).__init__(*args, **kwargs)
        if not self.content:
            # No need to specify the default content-type if we don't
            # have a body.
            del self['Content-Type']

    @http.HttpResponse.content.setter
    def content(self, value):
        # Delegate to django to actually set our content
        super(HttpResponse, self)._set_content(value)

        if self.content:
            # Hop in and set our content-length automatically because it just
            # feels right
            self['Content-Length'] = len(bytes(self.content))
