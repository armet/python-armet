# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.http import HttpResponse
from armet import http
from io import BytesIO
import re


# For almost all headers, django prefixes the header with `HTTP_`.  This is a
# list of headers that are an exception to that rule.
SPECIAL_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')


def _normalize(name):
    name = re.sub(r'^HTTP-', '', name.replace('_', '-'))
    name = http.request.Headers.normalize(name)
    return name


def _denormalize(name):
    name = name.replace('-', '_').upper()
    return name if name in SPECIAL_HEADERS else 'HTTP_' + name


class RequestHeaders(http.request.Headers):

    def __init__(self, handle):
        #! Reference to the underlying response handle.
        self._handle = handle

        # Continue the initialization.
        super(RequestHeaders, self).__init__()

    @staticmethod
    def normalize(name):
        # Proxy for internal usage of this.
        return _normalize(name)

    def __getitem__(self, name):
        return self._handle.META[_denormalize(name)]

    def __iter__(self):
        for name in self._handle.META:
            if name.startswith('HTTP_') or name in SPECIAL_HEADERS:
                yield self.normalize(name)

    def __len__(self):
        return sum(1 for x in self)

    def __contains__(self, name):
        return _denormalize(name) in self._handle.META


class Request(http.Request):

    def __init__(self, request, *args, **kwargs):
        # Store the request handle.
        self._handle = request

        # Initialize the request headers.
        self.headers = RequestHeaders(request)

        # Store a stream of the request.
        self._stream = BytesIO(request.body)

        # Set the method of the request.
        kwargs.update(method=self._handle.method)

        # Continue the initialization.
        super(Request, self).__init__(*args, **kwargs)

    def _read(self):
        return self._stream.read()

    @property
    def protocol(self):
        return self._handle.META['SERVER_PROTOCOL'].split('/')[0].upper()

    @property
    def mount_point(self):
        path = self._handle.path
        return path[:path.rfind(self.path)] if self.path else path

    @property
    def query(self):
        return self._handle.META.get('QUERY_STRING', '')

    @property
    def uri(self):
        return self._handle.build_absolute_uri()


class ResponseHeaders(http.response.Headers):

    def __init__(self, response, handle):
        #! Reference to the response object.
        self._response = response

        #! Reference to the underlying response handle.
        self._handle = handle

        # Continue the initialization.
        super(ResponseHeaders, self).__init__()

    def __getitem__(self, name):
        return self._handle[name]

    def __setitem__(self, name, value):
        self._response.require_open()
        self._handle[self.normalize(name)] = value

    def __delitem__(self, name):
        self._response.require_open()
        del self._handle[name]

    def __contains__(self, name):
        return self._handle.has_header(name)

    def __iter__(self):
        for name, _ in self._handle.items():
            yield name

    def __len__(self):
        return len(self._handle._headers)


class Response(http.Response):

    def __init__(self, *args, **kwargs):
        # Construct and store a new response object.
        self._handle = HttpResponse()

        # Complete the initialization.
        super(Response, self).__init__(*args, **kwargs)

        # If we're dealing with an asynchronous response, we need
        # to have an asynchronous queue to give to WSGI.
        if self.asynchronous:
            from gevent import queue
            self._queue = queue.Queue()

        # Initialize the response headers.
        self.headers = ResponseHeaders(self, self._handle)

    def __iter__(self):
        # Return the asynchronous queue.
        return self._queue

    @property
    def status(self):
        return self._handle.status_code

    @status.setter
    def status(self, value):
        self.require_open()
        self._handle.status_code = value

    @http.Response.body.setter
    def body(self, value):
        if value:
            if self.asynchronous:
                # Unset the underlying store.
                super(Response, Response).body.__set__(self, None)

                # Write the chunk to the asynchronous queue.
                self._queue.put(value)
                return

        # Set the underlying store.
        super(Response, Response).body.__set__(self, value)

    def close(self):
        # Perform general clean-up and a final flush.
        super(Response, self).close()

        if self.asynchronous:
            # Close the asynchronous queue and terminate the connection
            # to the client.
            self._queue.put(StopIteration)
