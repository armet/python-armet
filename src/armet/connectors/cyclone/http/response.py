# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.http import response
from six.moves import cStringIO as StringIO


class Headers(response.Headers):

    def __init__(self, response):
        self._handler = response._handler
        super(Headers, self).__init__(response)

    def __setitem__(self, name, value):
        self._response._assert_open()
        self._handler.set_header(self._normalize(name), value)

    def __getitem__(self, name):
        return self._handler._headers[self._normalize(name)]

    def __contains__(self, name):
        return self._normalize(name) in self._handler._headers

    def __delitem__(self, name):
        self._response._assert_open()
        self._handler.clear_header(self._normalize(name))

    def __len__(self):
        return len(self._handler._headers)

    def __iter__(self):
        return iter(self._handler._headers)


class Response(response.Response):

    def __init__(self, handler, *args, **kwargs):
        self._handler = handler
        self._stream = StringIO()
        self._length = 0
        kwargs.update(headers=Headers(self))
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
        self._length += self._stream.tell()
        self._stream.truncate(0)
        self._handler.flush()

    def _close(self):
        self._handler.write(self._stream.getvalue())
        self._handler.finish()
