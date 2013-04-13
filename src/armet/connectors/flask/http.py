# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http
from flask import request
from flask.globals import current_app
from werkzeug.wsgi import get_current_url


class Request(http.Request):

    @property
    def method(self):
        return request.method

    @method.setter
    def method(self, value):
        request.environ['REQUEST_METHOD'] = value.upper()

    @property
    def url(self):
        return get_current_url(request.environ)

    @property
    def path(self):
        return request.environ['PATH_INFO']

    @path.setter
    def path(self, value):
        request.environ['PATH_INFO'] = value

    def __getitem__(self, name):
        return request.headers.get(name)

    def __iter__(self):
        for key, _ in request.headers:
            yield key

    def __len__(self):
        return len(request.headers)

    def __contains__(self, name):
        return name in request.headers


class Response(http.Response):

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

    def __delitem__(self, name):
        del self.handle.headers[name]

    def __contains__(self, name):
        return name in self.handle.headers

    def __iter__(self):
        return iter(self.handle.headers)

    def __len__(self):
        return len(self.handle.headers)
