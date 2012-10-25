"""..
"""
from .http import HttpResponse


class Error(Exception):
    status = None

    def __init__(self, response=None):
        self.response = response or HttpResponse()
        self.response.status_code = self.status


class BadRequest(Error):
    status = 400


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
