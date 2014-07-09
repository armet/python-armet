from werkzeug.wrappers import BaseRequest, BaseResponse, ResponseStreamMixin


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


# class Request(BaseRequest):
#     pass


class Response(BaseResponse, ResponseStreamMixin):
    """There really doesn't need to be anything here."""
