# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.http import HttpResponse
from armet import http
import io
import re
from importlib import import_module


# For almost all headers, django prefixes the header with `HTTP_`.  This is a
# list of headers that are an exception to that rule.
SPECIAL_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')


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
        self._stream = io.BytesIO(self._handle.body)
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
        return self._stream.read(count).decode(self.encoding)

    def readline(self, limit=-1):
        return self._stream.readline(limit).decode(self.encoding)

    def readlines(self, hint=-1):
        encoding = self.encoding
        return [x.decode(encoding) for x in self._stream.readlines(hint)]


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
            return self._obj._handle.has_header(name)

        def __iter__(self):
            for name, _ in self._obj._handle.items():
                yield name

        def __len__(self):
            return len(self._obj._handle._headers)

    def __init__(self, *args, **kwargs):
        self._handle = HttpResponse()
        self._stream = io.BytesIO()
        super(Response, self).__init__(*args, **kwargs)
        if self.asynchronous:
            # If we're dealing with an asynchronous response, we need an
            # asynchronous queue to give to WSGI.
            self._queue = import_module('gevent.queue').Queue()

    @property
    def status(self):
        return self._handle.status_code

    @status.setter
    def status(self, value):
        self._assert_open()
        self._handle.status_code = value

    def clear(self):
        super(Response, self).clear()
        self._stream.truncate(0)
        self._stream.seek(0)

    def tell(self):
        self._assert_open()
        return self._stream.tell() + len(self._handle.content)

    def _write(self, chunk):
        self._stream.write(chunk)

    def _flush(self):
        if not self.asynchronous:
            # Nothing needs to be done as the write stream is doubling as
            # the output buffer.
            return

        # Write the buffer to the queue.
        self._queue.put(self._stream.getvalue())
        self._stream.truncate(0)
        self._stream.seek(0)

    def close(self):
        super(Response, self).close()
        if self.asynchronous:
            # Close the queue and terminate the connection.
            self._queue.put(StopIteration)
