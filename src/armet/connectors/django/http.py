# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.http import HttpResponse
from armet import utils, http


class Request(http.Request):
    """Implements the RESTFul request abstraction for django.
    """

    def __init__(self, request):
        self.handle = request

    @property
    @utils.memoize_single
    def method(self):
        override = self['X-Http-Method-Override']
        return override.upper() if override else self.handle.method

    @utils.memoize
    def __getitem__(self, name):
        name = name.replace('-', '_').upper()
        if name != 'CONTENT_TYPE':
            name = 'HTTP_{}'.format(name)
        return self.handle.META.get(name)


class Response(http.Response):
    """Implements the RESTFul response abstraction for django.
    """

    def __init__(self, *args, **kwargs):
        self.handle = HttpResponse()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self.handle.status_code

    @status.setter
    def status(self, value):
        self.handle.status_code = value

    def __getitem__(self, name):
        return self.handle.get(name)

    def __setitem__(self, name, value):
        self.handle[name] = value
