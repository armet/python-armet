from django import http
from .constants import *


class Response(http.HttpResponse):
    """Extends django's `HttpResponse` to more closely follow `HTTP/1.1`.
    """

    def __init__(self, *args, **kwargs):
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
