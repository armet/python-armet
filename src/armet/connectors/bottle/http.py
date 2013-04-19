# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
from six.moves import cStringIO as StringIO
import bottle


class Request(http.Request):

    class Headers(http.request.Headers):

        def __getitem__(self, name):
            return bottle.request.headers[name]

        def __iter__(self):
            return iter(bottle.request.headers)

        def __len__(self):
            return len(bottle.request.headers)

        def __contains__(self, name):
            return name in bottle.request.headers

    def __init__(self, *args, **kwargs):
        kwargs.update(method=bottle.request.method)
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return bottle.request.urlparts.scheme.upper()

    @property
    def host(self):
        return self.headers.get('Host') or '127.0.0.1'

    @property
    def query(self):
        return bottle.request.query_string

    @property
    def uri(self):
        return bottle.request.url

    def read(self, count=-1):
        return bottle.request.body.read(count)

    def readline(self, limit=-1):
        return bottle.request.body.readline(limit)

    def readlines(self, hint=-1):
        return bottle.request.body.readlines(hint)


class Response(http.Response):

    class Headers(http.response.Headers):

        def __setitem__(self, name, value):
            self._obj._assert_open()
            bottle.response.headers[self._normalize(name)] = value

        def __getitem__(self, name):
            return bottle.response.headers[name]

        def __contains__(self, name):
            return name in bottle.response.headers

        def __delitem__(self, name):
            self._obj._assert_open()
            del bottle.response.headers[self._normalize(name)]

        def __len__(self):
            return len(bottle.response.headers)

        def __iter__(self):
            return iter(bottle.response.headers)

    def __init__(self, *args, **kwargs):
        self._stream = StringIO()
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return bottle.response.status_code

    @status.setter
    def status(self, value):
        self._assert_open()
        bottle.response.status = value

    def tell(self):
        return self._stream.tell() + len(bottle.response.body)

    def _write(self, chunk):
        self._stream.write(chunk)

    def _flush(self):
        raise NotImplementedError()

    def close(self):
        super(Response, self).close()
        bottle.response.body = self._stream.getvalue()
