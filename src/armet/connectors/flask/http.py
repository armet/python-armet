# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
from armet import http
import flask
import io
from flask.globals import current_app
from werkzeug.wsgi import get_current_url, LimitedStream
from importlib import import_module


class Request(http.Request):

    class Headers(http.request.Headers):

        def __getitem__(self, name):
            return self._obj._handle.headers[name]

        def __iter__(self):
            return (key for key, _ in self._obj._handle.headers)

        def __len__(self):
            return len(self._obj._handle.headers)

        def __contains__(self, name):
            return name in self._obj._handle.headers

    def __init__(self, *args, **kwargs):
        request = flask.request
        async = kwargs['asynchronous']
        self._handle = request if not async else flask.Request(request.environ)
        kwargs.update(method=self._handle.method)
        super(Request, self).__init__(*args, **kwargs)
        self._stream = LimitedStream(self._handle.input_stream, len(self))

    @property
    def protocol(self):
        return self._handle.scheme.upper()

    @property
    def mount_point(self):
        if self.path:
            return self._handle.path.rsplit(self.path)[0]

        return self._handle.path

    @property
    def query(self):
        if isinstance(self._handle.query_string, six.binary_type):
            return self._handle.query_string.decode('utf8')

        return self._handle.query_string

    @property
    def uri(self):
        return get_current_url(self._handle.environ)

    def _read(self, count=-1):
        return self._stream.read(count)

    def _readline(self, limit=-1):
        return self._stream.readline(limit)

    def _readlines(self, hint=-1):
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
            return (key for key, _ in self._obj._handle.headers)

        def __len__(self):
            return len(self._obj._handle.headers)

    def __init__(self, *args, **kwargs):
        self._handle = current_app.response_class()
        self._stream = io.BytesIO()
        super(Response, self).__init__(*args, **kwargs)
        if self.asynchronous:
            # If we're dealing with an asynchronous response, we need an
            # asynchronous queue to give to WSGI.
            self._queue = import_module('gevent.queue').Queue()

    @property
    def status(self):
        return self._handle.status_code

    def clear(self):
        super(Response, self).clear()
        self._stream.truncate(0)
        self._stream.seek(0)

    @status.setter
    def status(self, value):
        self._assert_open()
        self._handle.status_code = value

    def tell(self):
        return self._stream.tell() + len(self._handle.data)

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
