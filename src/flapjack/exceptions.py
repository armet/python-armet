"""..
"""
from django.http import HttpResponse


class Error(Exception):
    status = 400

    def __init__(self, response=None):
        self.response = response or HttpResponse()
        self.response.status_code = self.status


class NotAcceptable(Error):
    status = 406


class MethodNotAllowed(Error):
    status = 405


class UnsupportedMediaType(Error):
    status = 415


class NotImplemented(Error):
    status = 501
