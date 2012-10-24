""" ..
"""
from django import http


class HttpResponse(http.HttpResponse):
    """ ..
    """

    def __init__(self, *args, **kwargs):
        super(HttpResponse, self).__init__(*args, **kwargs)
        if not self.content:
            # No need to specify the default content-type if we don't
            # have a body.
            del self['Content-Type']
