# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http
import six
import bottle

if six.PY3:
    from urllib.parse import SplitResult as UrlSplitResult

else:
    from urlparse import SplitResult as UrlSplitResult


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

    @property
    def path(self):
        return bottle.request.environ['PATH_INFO']

    @path.setter
    def path(self, value):
        bottle.request.environ['PATH_INFO'] = value
        key = 'bottle.request.urlparts'
        bottle.request.url
        parts = bottle.request.environ[key]._asdict()
        parts['path'] = value
        bottle.request.environ[key] = UrlSplitResult(**parts)

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

    @property
    def content(self):
        return bottle.response.body

    @content.setter
    def content(self, value):
        bottle.response.body = value if value is not None else ''

    def __getitem__(self, name):
        return bottle.response.headers[name]

    def __setitem__(self, name, value):
        bottle.response.headers[name] = value

    def __delitem__(self, name):
        del bottle.response.headers[name]

    def __contains__(self, name):
        return name in bottle.response.headers

    def __iter__(self):
        return iter(bottle.response.headers)

    def __len__(self):
        return len(bottle.response.headers)
