# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import utils
from armet.http.request import Request
from armet.http.response import Response
from flask import request
from flask.globals import current_app


class Request(Request):
    """Implements the RESTFul request abstraction for flask.
    """

    @property
    @utils.memoize_single
    def method(self):
        override = self['X-Http-Method-Override']
        return override.upper() if override else request.method

    def __getitem__(self, name):
        return request.headers.get(name)

    def __iter__(self):
        for key, _ in request.headers:
            yield key

    def __len__(self):
        return len(request.headers)


class Response(Response):
    """Implements the RESTFul response abstraction for flask.
    """

    def __init__(self, *args, **kwargs):
        self.handle = current_app.response_class()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self.handle.status_code

    @status.setter
    def status(self, value):
        self.handle.status_code = value

    @property
    def content(self):
        return self.handle.data

    @content.setter
    def content(self, value):
        self.handle.data = value if value is not None else ''

    def __getitem__(self, name):
        return self.handle.headers[name]

    def __setitem__(self, name, value):
        self.handle.headers[name] = value
