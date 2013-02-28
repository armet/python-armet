# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet.http import client


class Base(BaseException):
    status = None

    def __init__(self, content=None, headers=None):
        #! Body of the exception message.
        self.content = content

        #! Additional headers to place with the response.
        self.headers = headers or {}


class NotFound(Base):
    status = client.NOT_FOUND


class MethodNotAllowed(Base):
    status = client.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        super(MethodNotAllowed, self).__init__(
            headers={'Allowed': ', '.join(allowed)})


class NotImplemented(Base):
    status = client.NOT_IMPLEMENTED
