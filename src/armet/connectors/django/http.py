# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.http import HttpResponse
from armet import http
from six.moves import cStringIO as StringIO
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

def _normalize(name):
    name = re.sub(r'^HTTP-', '', name.replace('_', '-'))
    name = Request.Headers._normalize(name)
    return name


def _denormalize(name):
    name = name.replace('-', '_').upper()
    return name if name in SPECIAL_HEADERS else 'HTTP_' + name


class Request(http.Request):

    class Headers(http.request.Headers):

        @staticmethod
        def _normalize(name):
            # Proxy for internal usage of this.
            return _normalize(name)

        def __getitem__(self, name):
            return self._obj._handle.META[_denormalize(name)]

        def __iter__(self):
            for name in self._obj._handle.META:
                if name.startswith('HTTP_') or name in SPECIAL_HEADERS:
                    yield self._normalize(name)

        def __len__(self):
            return sum(1 for x in self)

        def __contains__(self, name):
            return _denormalize(name) in self._obj._handle.META

    def __init__(self, request, *args, **kwargs):
        self._handle = request
        self._stream = StringIO(self._handle.body)
        kwargs.update(method=self._handle.method)
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return self._handle.META['SERVER_PROTOCOL'].split('/')[0].upper()

    @property
    def query(self):
        return self._handle.META.get('QUERY_STRING', '')

    @property
    def uri(self):
        return self._handle.build_absolute_uri()

    def read(self, count=-1):
        return self._stream.read(count)

    def readline(self, limit=-1):
        return self._stream.readline(limit)

    def readlines(self, hint=-1):
        return self._stream.readlines(hint)


class Response(http.Response):

    class Headers(http.response.Headers):

        def __getitem__(self, name):
            return self._obj._handle[name]

        def __setitem__(self, name, value):
            self._obj._assert_open()
            self._obj._handle[self._normalize(name)] = value

        def __delitem__(self, name):
            self._obj._assert_open()
            del self._obj._handle[name]

        def __contains__(self, name):
            return name in self._obj._handle

        def __iter__(self):
            return iter(self._obj._handle)

        def __len__(self):
            return len(self._obj._handle)

    def __init__(self, *args, **kwargs):
        self._handle = HttpResponse()
        self._stream = StringIO()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self._handle.status_code

    @status.setter
    def status(self, value):
        self._assert_open()
        self._handle.status_code = value

    def tell(self):
        self._assert_open()
        return self._stream.tell() + len(self._handle.content)

    def _write(self, chunk):
        self._stream.write(chunk)

    def _flush(self):
        # Nothing needs to be done as the write stream is doubling as
        # the output buffer.
        return

    def close(self):
        super(Response, self).close()
        self._handle.content = self._stream.getvalue()
