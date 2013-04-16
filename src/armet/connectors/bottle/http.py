# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http
import bottle


class Request(http.Request):

    @property
    def method(self):
        return bottle.request.method

    @method.setter
    def method(self, value):
        bottle.request.environ['REQUEST_METHOD'] = value

    @property
    def url(self):
        return bottle.request.url

    def __getitem__(self, name):
        return bottle.request.headers.get(name)

    def __iter__(self):
        for key, _ in bottle.request.headers:
            yield key

    def __len__(self):
        return len(bottle.request.headers)

    def __contains__(self, name):
        return name in bottle.request.headers


class Response(http.Response):

    @property
    def status(self):
        return bottle.response.status_code

    @status.setter
    def status(self, value):
        bottle.response.status = value

    def write(self, value):
        if value is not None:
            bottle.response.body += value

    def __getitem__(self, name):
        return bottle.response.headers[str(name)]

    def __setitem__(self, name, value):
        bottle.response.headers[str(name)] = value

    def __delitem__(self, name):
        del bottle.response.headers[str(name)]

    def __contains__(self, name):
        return str(name) in bottle.response.headers

    def __iter__(self):
        return iter(bottle.response.headers)

    def __len__(self):
        return len(bottle.response.headers)
