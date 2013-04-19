# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.http import request
from six.moves import cStringIO as StringIO


class Headers(request.Headers):

    def __init__(self, handle):
        self.__handle = handle
        super(Headers, self).__init__()

    def __getitem__(self, name):
        return self.__handle.headers[name]

    def __iter__(self):
        return iter(self.__handle.headers)

    def __len__(self):
        return len(self.__handle.headers)

    def __contains__(self, name):
        return name in self.__handle.headers


class Request(request.Request):

    def __init__(self, handler, *args, **kwargs):
        self.__handle = handler.request
        self.__stream = StringIO(self.__handle.body)
        kwargs.update(method=self.__handle.method,
                      headers=Headers(self.__handle))
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return self.__handle.protocol.upper()

    @property
    def host(self):
        return self.__handle.host

    @property
    def query(self):
        return self.__handle.query

    @property
    def uri(self):
        return self.__handle.full_url()

    def read(self, count=-1):
        return self.__stream.read(count)

    def readline(self, limit=-1):
        return self.__stream.readline(limit)

    def readlines(self, hint=-1):
        return self.__stream.readlines(hint)
