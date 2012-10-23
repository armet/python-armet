"""..
"""
from django.http import HttpResponse


class Error(Exception):
    status = 400

    def __init__(self, response=None):
        if response is not None:
            self.response = response
        else:
            self.response = HttpResponse()

        self.response.status_code = self.status

        if not self.response.content:
            # No need to specify the default content-type if we don't
            # have a body.
            del self.response['Content-Type']


class NotAcceptable(Error):
    status = 406


class MethodNotAllowed(Error):
    status = 405


class UnsupportedMediaType(Error):
    status = 415


class NotImplemented(Error):
    status = 501
