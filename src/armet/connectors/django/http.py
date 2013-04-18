# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.http import HttpResponse
from armet import http
import string
import re

# For almost all headers, django prefixes the header with `HTTP_`.  This is a
# list of headers that are an exception to that rule.
SPECIAL_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')


def from_django(name):
    """De-djangoifies the name of a header."""
    name = re.sub(r'^HTTP_', '', name)
    name = re.sub(r'_', '-', name)
    return string.capwords(name.lower(), '-')


def to_django(name):
    """Djangoifies the name of a header."""
    name = name.replace('-', '_').upper()
    return name if name in SPECIAL_HEADERS else 'HTTP_{}'.format(name)


class Request(http.Request):

    def __init__(self, request, *args, **kwargs):
        self.handle = request
        super(Request, self).__init__(*args, **kwargs)

    @property
    def method(self):
        return self.handle.method

    @method.setter
    def method(self, value):
        self.handle.method = value.upper()

    @property
    def url(self):
        return self.handle.get_full_path()

    def __getitem__(self, name):
        return self.handle.META[to_django(name)]

    def __iter__(self):
        for name in self.handle.META:
            if name.startswith('HTTP_') or name in SPECIAL_HEADERS:
                yield from_django(name)

    def __len__(self):
        return sum(1 for x in self)

    def __contains__(self, name):
        return to_django(name) in self.handle.META


class Response(http.Response):

    def __init__(self, *args, **kwargs):
        self.handle = HttpResponse()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self.handle.status_code

    @status.setter
    def status(self, value):
        self.handle.status_code = value

    def write(self, value):
        if value is not None:
            self.handle.content += value

    def __getitem__(self, name):
        return self.handle[name]

    def __setitem__(self, name, value):
        self.handle[name] = value

    def __delitem__(self, name):
        del self.handle[name]

    def __contains__(self, name):
        return name in self.handle

    def __iter__(self):
        return iter(self.handle)

    def __len__(self):
        return len(self.handle)
