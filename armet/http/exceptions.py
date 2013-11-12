# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.http import client


class BaseHTTPException(BaseException):
    status = None

    def __init__(self, content=None, headers=None):
        #! Body of the exception message.
        self.content = content

        #! Additional headers to place with the response.
        self.headers = headers or {}


class BadRequest(BaseHTTPException):
    status = client.BAD_REQUEST


class Forbidden(BaseHTTPException):
    status = client.FORBIDDEN


class NotFound(BaseHTTPException):
    status = client.NOT_FOUND


class MethodNotAllowed(BaseHTTPException):
    status = client.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        super(MethodNotAllowed, self).__init__(
            headers={'Allow': ', '.join(allowed)})


class NotAcceptable(BaseHTTPException):
    status = client.NOT_ACCEPTABLE


class UnsupportedMediaType(BaseHTTPException):
    status = client.UNSUPPORTED_MEDIA_TYPE


class InternalServerError(BaseHTTPException):
    status = client.INTERNAL_SERVER_ERROR


class NotImplemented(BaseHTTPException):
    status = client.NOT_IMPLEMENTED
