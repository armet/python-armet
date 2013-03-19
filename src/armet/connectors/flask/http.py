# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import resources, utils
from flask import request
from flask.globals import current_app


class Request(resources.Request):
    """Implements the RESTFul request abstraction for flask.
    """

    @property
    @utils.memoize_single
    def method(self):
        override = self.header('X-Http-Method-Override')
        return override.upper() if override else request.method

    @utils.memoize
    def __getitem__(self, name):
        return request.headers.get(name)


class Response(resources.Response):
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

    def __getitem__(self, name):
        return self.handle.headers[name]

    def __setitem__(self, name, value):
        self.handle.headers[name] = value
