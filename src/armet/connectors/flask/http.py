# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
import flask
from six.moves import cStringIO as StringIO
from flask.globals import current_app
from werkzeug.wsgi import get_current_url, LimitedStream


class Request(http.Request):

    class Headers(http.request.Headers):

        def __getitem__(self, name):
            return flask.request.headers.get(name)

        def __iter__(self):
            return (key for key, _ in flask.request.headers)

        def __len__(self):
            return len(flask.request.headers)

        def __contains__(self, name):
            return name in flask.request.headers

    def __init__(self, *args, **kwargs):
        kwargs.update(method=flask.request.method)
        super(Request, self).__init__(*args, **kwargs)
        self._stream = LimitedStream(flask.request.input_stream, len(self))

    @property
    def protocol(self):
        return flask.request.scheme.upper()

    @property
    def query(self):
        return flask.request.query_string

    @property
    def uri(self):
        return get_current_url(flask.request.environ)

    def read(self, count=-1):
        return self._stream.read(count)

    def readline(self, limit=-1):
        return self._stream.readline(limit)

    def readlines(self, hint=-1):
        return self._stream.readlines(hint)


class Response(http.Response):

    class Headers(http.response.Headers):

        def __getitem__(self, name):
            return self._obj._handle.headers[name]

        def __setitem__(self, name, value):
            self._obj._assert_open()
            self._obj._handle.headers[self._normalize(name)] = value

        def __contains__(self, name):
            return name in self._obj._handle.headers

        def __delitem__(self, name):
            self._obj._assert_open()
            del self._obj._handle.headers[name]

        def __iter__(self):
            return iter(self._obj._handle.headers)

        def __len__(self):
            return len(self._obj._handle.headers)

    def __init__(self, *args, **kwargs):
        self._handle = current_app.response_class()
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
        return self._stream.tell() + len(self._handle.data)

    def _write(self, chunk):
        self._stream.write(chunk)

    def _flush(self):
        raise NotImplementedError()

    def close(self):
        super(Response, self).close()
        self._handle.data = self._stream.getvalue()
