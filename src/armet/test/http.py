# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
import io


class Request(http.Request):

    class Headers(http.request.Headers):

        def __getitem__(self, name):
            return self._obj._headers[name]

        def __iter__(self):
            return iter(self._obj._headers)

        def __len__(self):
            return len(self._obj._headers)

        def __contains__(self, name):
            return name in self._obj._headers

    def __init__(self, *args, **kwargs):
        self._stream = io.BytesIO(kwargs.pop('content', ''))
        self._headers = kwargs.pop('headers', {})
        self._protocol = kwargs.pop('protocol', 'HTTP')
        self._mount_point = kwargs.pop('mount_point', '')
        self._query = kwargs.pop('query', '/')
        self._uri = kwargs.pop('uri', '/')
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return self._protocol

    @property
    def mount_point(self):
        return self._mount_point

    @property
    def query(self):
        return self._query

    @property
    def uri(self):
        return '{}://{}{}{}'.format(self._protocol,
                                    self._mount_point,
                                    self.path,
                                    self._query)

    def _read(self, count=-1):
        return self._stream.read(count)

    def _readline(self, limit=-1):
        return self._stream.readline(limit)

    def _readlines(self, hint=-1):
        return self._stream.readlines(hint)


class Response(http.Response):

    class Headers(http.response.Headers):

        def __init__(self, *args, **kwargs):
            self._store = {}
            super(Response.Headers, self).__init__(*args, **kwargs)

        def __setitem__(self, name, value):
            self._obj._assert_open()
            self._store[self._normalize(name)] = value

        def __getitem__(self, name):
            return self._store[self._normalize(name)]

        def __contains__(self, name):
            return self._normalize(name) in self._store

        def __delitem__(self, name):
            self._obj._assert_open()
            del self._store[self._normalize(name)]

        def __len__(self):
            return len(self._store)

        def __iter__(self):
            return iter(self._store)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('asynchronous', False)
        self.stream = io.BytesIO()
        super(Response, self).__init__(*args, **kwargs)

    def clear(self):
        self._closed = False
        self._streaming = False
        super(Response, self).clear()
        self.content = ''
        self.stream.truncate(0)
        self.stream.seek(0)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._assert_open()
        self._status = value

    def tell(self):
        return self.stream.tell() + len(self.content)

    def _write(self, chunk):
        self.stream.write(chunk)

    def _flush(self):
        raise NotImplementedError()

    def close(self):
        super(Response, self).close()
        self.content = self.stream.getvalue()
