# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.http import HttpResponse
from armet import utils
from armet.http import request, response
import string


# For almost all headers, django prefixes the header with `HTTP_`.  This is a
# list of headers that are an exception to that rule.
SPECIAL_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')


def from_django(name):
    """De-djangoifies the name of a header."""

    # Strip off the HTTP prefix
    prefix = 'HTTP_'
    if name.startswith(prefix):
        name = name.lstrip(prefix)

    # Go from 'CONTENT_TYPE' to 'Content-Type'
    name = name.lower().replace('_', '-')
    return string.capwords(name, '-')


def to_django(name):
    """Djangoifies the name of a header."""
    name = name.replace('-', '_').upper()

    if name not in SPECIAL_HEADERS:
        return 'HTTP_{}'.format(name)
    return name


class Request(request.Request):
    """Implements the RESTFul request abstraction for django.
    """

    def __init__(self, request):
        self.handle = request

    @property
    @utils.memoize_single
    def method(self):
        override = self['X-Http-Method-Override']
        return override.upper() if override else self.handle.method

    def __getitem__(self, name):
        return self.handle.META.get(to_django(name))

    def __iter__(self):
        """Iterate over all the headers in the request."""
        for name in self.handle.META:

            # META items beginning with 'HTTP_' are always headers.
            if name.startswith('HTTP_') or name in SPECIAL_HEADERS:
                yield from_django(name)

    def __len__(self):
        """Return the number of headers that are available."""
        return sum(1 for x in self)


class Response(response.Response):
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

    @property
    def content(self):
        return self.handle.content if self.handle.content else ''

    @content.setter
    def content(self, value):
        self.handle.content = value if value is not None else ''

    def __getitem__(self, name):
        return self.handle.get(name)

    def __setitem__(self, name, value):
        self.handle[name] = value
