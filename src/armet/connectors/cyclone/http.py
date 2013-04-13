# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http
from armet.http import request, response


class Request(request.Request):
    """Implements the request abstraction for cyclone.
    """

    def __init__(self, handler, *args, **kwargs):
        self.handler = handler

        # This is the python request object
        self.request = handler.request

        super(Request, self).__init__(*args, **kwargs)

    @property
    def url(self):
        return self.request.full_url()

    @property
    def path(self):
        return self.request.path

    @path.setter
    def path(self, value):
        self.request.path = value

    @property
    def method(self):
        return self.request.method

    @method.setter
    def method(self, value):
        self.request.method = value.upper()

    def __getitem__(self, name):
        return self.request.headers[name]

    def __iter__(self):
        return iter(self.request.headers)

    def __len__(self):
        return len(self.request.headers)

    def __contains__(self, item):
        return item in self.request.headers


class Response(response.Response):
    """Implements the response abstraction for cyclone.
    """

    def __init__(self, resource, *args, **kwargs):
        self.resource = resource
        self.handler = resource.request.handler

        # Initialize caches for the status code and the body of the response
        self._status = http.client.OK
        self._content = ''

        super(Response, self).__init__(*args, **kwargs)

    def __setitem__(self, name, value):
        self.handler.set_header(name, value)

    def __getitem__(self, name):
        # Cyclone doesn't provide a way to get headers normally, so break
        # into the private methods to retrieve the header.  Note that
        # this doesn't retrieve multi-value headers.  However, armet should
        # handle multi-value wrangling itself.
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
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
