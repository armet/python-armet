# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
import bottle


class RequestHeaders(http.request.Headers):

    def __getitem__(self, name):
        return bottle.request.headers[name]

    def __iter__(self):
        return iter(bottle.request.headers)

    def __len__(self):
        return len(bottle.request.headers)

    def __contains__(self, name):
        return name in bottle.request.headers


class Request(http.Request):

    def __init__(self, *args, **kwargs):
        # Initialize the request headers.
        self.headers = RequestHeaders()

        # Set the method of the request.
        request = bottle.request
        kwargs.update(method=request.method)

        # Elide the thread-safe request copy and the global bottle.request.
        self._handle = request.copy() if kwargs['asynchronous'] else request

        # Continue the initialization.
        super(Request, self).__init__(*args, **kwargs)

    def _read(self):
        return self._handle.body.read()

    @property
    def protocol(self):
        return self._handle.urlparts.scheme.upper()

    @property
    def mount_point(self):
        path = self._handle.path
        return path[:path.rfind(self.path)] if self.path else path

    @property
    def query(self):
        return self._handle.query_string

    @property
    def uri(self):
        return self._handle.url


class ResponseHeaders(http.response.Headers):

    def __init__(self, response, handle):
        #! Reference to the response object.
        self._response = response

        #! Reference to the underlying response handle.
        self._handle = handle

        # Continue the initialization.
        super(ResponseHeaders, self).__init__()

    def __setitem__(self, name, value):
        self._response.require_open()
        self._handle.headers[self.normalize(name)] = value

    def __getitem__(self, name):
        return self._handle.headers[name]

    def __contains__(self, name):
        return name in self._handle.headers

    def __delitem__(self, name):
        self._response.require_open()
        del self._handle.headers[name]

    def __len__(self):
        return len(self._handle.headers)

    def __iter__(self):
        return iter(self._handle.headers)


class Response(http.Response):

    def __init__(self, *args, **kwargs):
        # Elide the thread-safe response copy and the global bottle.response.
        self._handle = bottle.response

        # Complete the initialization.
        super(Response, self).__init__(*args, **kwargs)

        # If we're dealing with an asynchronous response, we need
        # to have a thread-safe response handle as well as an
        # asynchronous queue to give to WSGI.
        if self.asynchronous:
            from gevent import queue

            self._handle = self._handle.copy()
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
        self._handle.status = value

    @http.Response.body.setter
    def body(self, value):
        if value:
            if not self.streaming:
                # Point the response handle to our constructed response.
                bottle.response.status = self.status
                bottle.response.headers.update(self.headers)

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
