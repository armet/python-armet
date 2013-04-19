# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
from six.moves import cStringIO as StringIO
from twisted.internet import reactor


class Request(http.Request):

    class Headers(http.request.Headers):

        def __init__(self, request):
            self._handle = request._handle
            super(Request.Headers, self).__init__(request)

        def __getitem__(self, name):
            return self._handle.headers[name]

        def __iter__(self):
            return iter(self._handle.headers)

        def __len__(self):
            return len(self._handle.headers)

        def __contains__(self, name):
            return name in self._handle.headers

    def __init__(self, handler, *args, **kwargs):
        self._handle = handler.request
        self._stream = StringIO(self._handle.body)
        kwargs.update(method=self._handle.method)
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return self._handle.protocol.upper()

    @property
    def query(self):
        return self._handle.query

    @property
    def uri(self):
        return self._handle.full_url()

    def read(self, count=-1):
        return self._stream.read(count)

    def readline(self, limit=-1):
        return self._stream.readline(limit)

    def readlines(self, hint=-1):
        return self._stream.readlines(hint)


class Response(http.Response):

    class Headers(http.response.Headers):

        def __init__(self, response):
            self._handler = response._handler
            super(Response.Headers, self).__init__(response)

        def __setitem__(self, name, value):
            self._obj._assert_open()
            self._handler.set_header(self._normalize(name), value)

        def __getitem__(self, name):
            return self._handler._headers[name]

        def __contains__(self, name):
            return name in self._handler._headers

        def __delitem__(self, name):
            self._obj._assert_open()
            self._handler.clear_header(name)

        def __len__(self):
            return len(self._handler._headers)

        def __iter__(self):
            return iter(self._handler._headers)

    def __init__(self, handler, *args, **kwargs):
        self._handler = handler
        self._stream = StringIO()
        self._length = 0
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self._handler.get_status()

    @status.setter
    def status(self, value):
        self._assert_open()
        self._handler.set_status(value)

    def tell(self):
        return self._stream.tell() + self._length

    def _write(self, chunk):
        self._stream.write(chunk)

    def _flush(self):
        self._handler.write(self._stream.getvalue())
        self._stream.truncate(0)
        self._handler.flush()

    def close(self):
        super(Response, self).close()
        self._handler.write(self._stream.getvalue())
        self._handler.finish()
