"""..
"""
from six.moves import http_client
from . import http, encoders


class Error(Exception):
    status = None

    def __init__(self, content=None, headers=None):
        #! Body of the exception message.
        self.content = content

        #! Additional headers to place with the response.
        self.headers = headers or {}

    def dispatch(self, encoder=None):
        response = http.Response()
        if self.content:
            if encoder is None:
                # TODO: Change this to text when possible
                encoder = encoders.Json()

            response.content = encoder.encode(self.content)
            response['Content-Type'] = encoder.mimetype

        for header in self.headers:
            response[header] = self.headers[header]

        response.status_code = self.status
        return response


class BadRequest(Error):
    status = http_client.BAD_REQUEST


class Unauthorized(Error):
    status = http_client.UNAUTHORIZED

    def __init__(self, realm):
        super(Unauthorized, self).__init__(headers={
            'WWW-Authenticate': 'Basic Realm="{}"'.format(realm)})


class Forbidden(Error):
    status = http_client.FORBIDDEN


class NotFound(Error):
    status = http_client.NOT_FOUND


class NotAcceptable(Error):
    status = http_client.NOT_ACCEPTABLE


class MethodNotAllowed(Error):
    status = http_client.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        super(MethodNotAllowed, self).__init__(headers={'Allow': allowed})


class UnsupportedMediaType(Error):
    status = http_client.UNSUPPORTED_MEDIA_TYPE


class NotImplemented(Error):
    status = http_client.NOT_IMPLEMENTED


class AuthenticationRequired(Error):
    status = http_client.AUTHENTICATION_REQUIRED
