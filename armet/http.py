from werkzeug.wrappers import BaseRequest


class Request:

    def __init__(self, environ):
        self._handle = BaseRequest(environ, populate_request=False)

    @property
    def method(self):
        return self._handle.method

    @property
    def path(self):
        return self._handle.path

    @property
    def headers(self):
        return self._handle.headers
