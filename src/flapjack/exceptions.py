"""..
"""
from . import http


class Error(Exception):
    status = None

    def __init__(self, content=None):
        #! Body of the exception message.
        self.content = content


class BadRequest(Error):
    status = http.BAD_REQUEST


class NotFound(Error):
    status = 404


class NotAcceptable(Error):
    status = 406


class MethodNotAllowed(Error):
    status = 405


class UnsupportedMediaType(Error):
    status = 415


class NotImplemented(Error):
    status = 501
