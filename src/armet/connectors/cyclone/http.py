# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http


class RequestHeaders(http.request.Headers):

    def __init__(self, handle):
        #! Reference to the underlying request handle.
        self._handle = handle

        # Continue the initialization.
        super(RequestHeaders, self).__init__()

    def __getitem__(self, name):
        return self._handle.headers[name]

    def __iter__(self):
        return iter(self._handle.headers)

    def __len__(self):
        return len(self._handle.headers)

    def __contains__(self, name):
        return name in self._handle.headers


class Request(http.Request):

    def __init__(self, handler, *args, **kwargs):
        # Store the request handle.
        self._handle = handler.request

        # Initialize the request headers.
        self.headers = RequestHeaders(self._handle)

        # Set the method and body of the request.
        kwargs.update(body=self._handle.body)
        kwargs.update(method=self._handle.method)

        # Continue the initialization.
        super(Request, self).__init__(*args, **kwargs)

    @property
    def protocol(self):
        return self._handle.protocol.upper()

    @property
    def mount_point(self):
        path = self._handle.path
        return path.rsplit(self.path)[0] if self.path else path

    @property
    def query(self):
        return self._handle.query

    @property
    def uri(self):
        return self._handle.full_url()


class ResponseHeaders(http.response.Headers):

    def __init__(self, response, handler):
        #! Reference to the response object.
        self._response = response

        #! Reference to the underlying response handler.
        self._handler = handler

        # Continue the initialization.
        super(ResponseHeaders, self).__init__()

    def __setitem__(self, name, value):
        self._response.require_open()
        self._handler.set_header(self.normalize(name), value)

    def __getitem__(self, name):
        return self._handler._headers[name]

    def __contains__(self, name):
        return name in self._handler._headers

    def __delitem__(self, name):
        self._response.require_open()
        self._handler.clear_header(name)

    def __len__(self):
        return len(self._handler._headers)

    def __iter__(self):
        return iter(self._handler._headers)


class Response(http.Response):

    def __init__(self, handler, *args, **kwargs):
        # Store the handler.
        self._handler = handler

        # Initialize the response headers.
        self.headers = ResponseHeaders(self, handler)

        # Complete the initialization.
        super(Response, self).__init__(*args, **kwargs)

    @property
    def status(self):
        return self._handler.get_status()

    @status.setter
    def status(self, value):
        self.require_open()
        self._handler.set_status(value)

    @http.Response.body.setter
    def body(self, value):
        if value:
            # Write out the value.
            self._handler.write(value)

            if self.asynchronous or self.streaming:
                # Unset the underlying store.
                super(Response, Response).body.__set__(self, None)

                # Flush what we have.
                self._handler.flush()
                return

        # Set the underlying store.
        super(Response, Response).body.__set__(self, value)

    def close(self):
        # Perform general clean-up and a final flush.
        super(Response, self).close()

        if self.asynchronous:
            # Close the asynchronous queue and terminate the connection
            # to the client.
            self._handler.finish()
