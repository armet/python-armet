# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http


class Request(http.Request):

    def __init__(self, handler, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.handle = handler.request

    @property
    def url(self):
        return self.handle.full_url()

    @property
    def method(self):
        return self.handle.method

    @method.setter
    def method(self, value):
        self.handle.method = value.upper()

    def __getitem__(self, name):
        return self.handle.headers[name]

    def __iter__(self):
        return iter(self.handle.headers)

    def __len__(self):
        return len(self.handle.headers)

    def __contains__(self, item):
        return item in self.handle.headers


class Response(http.Response):

    def __init__(self, handler, *args, **kwargs):
        super(Response, self).__init__(*args, **kwargs)
        self.handler = handler

    def __setitem__(self, name, value):
        self.handler.set_header(name, value)

    def __getitem__(self, name):
        # Cyclone doesn't provide a way to get headers normally, so break
        # into the private methods to retrieve the header.
        return self.handler._headers[name]

    def __contains__(self, name):
        return name in self.handler._headers

    def __delitem__(self, name):
        self.handler.clear_header(name)

    def __len__(self):
        return len(self.handler._headers)

    def __iter__(self):
        return iter(self.handler._headers)

    @property
    def status(self):
        return self.handler.get_status()

    @status.setter
    def status(self, value):
        self.handler.set_status(value)

    def write(self, chunk):
        self.handler.write(chunk)
