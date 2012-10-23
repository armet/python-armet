""" ..
"""
from django import http


class HttpResponse(http.HttpResponse):
    """ ..
    """

    def serialize(self):
        if not self.content:
            # No need to specify the default content-type if we don't
            # have a body.
            del self['Content-Type']

        # Delegate to django to serialize ourself
        super(HttpResponse, self).serialize()
