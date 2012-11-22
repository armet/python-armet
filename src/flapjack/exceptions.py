"""..
"""
from .http import status, HttpResponse


class Error(Exception):
    status = None

    def __init__(self, content=None):
        #! Body of the exception message.
        self.content = content

    def encode(self, encoder):
        if self.content:
            response = encoder.encode(self.content)
        else:
            response = HttpResponse()

        response.status_code = self.status
        return response


class BadRequest(Error):
    status = status.BAD_REQUEST


class Forbidden(Error):
    status = status.FORBIDDEN


class NotFound(Error):
    status = status.NOT_FOUND


class NotAcceptable(Error):
    status = status.NOT_ACCEPTABLE


class MethodNotAllowed(Error):
    status = status.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        self.allowed = allowed
        super(MethodNotAllowed, self).__init__()

    def encode(self, encoder):
        response = super(MethodNotAllowed, self).encode(encoder)
        response['Allow'] = self.allowed
        return response


class UnsupportedMediaType(Error):
    status = status.UNSUPPORTED_MEDIA_TYPE


class NotImplemented(Error):
    status = status.NOT_IMPLEMENTED
