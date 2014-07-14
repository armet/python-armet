from werkzeug import exceptions
from http import client
from collections import OrderedDict

# Mirrors to werkzeug exceptions in the event we need to overload
# these ourselves.
Base = exceptions.HTTPException


class Base(exceptions.HTTPException):

    def get_body(self, environ=None):
        # There is no body that needs to be returned for api exceptions.
        return ''

    def get_headers(self, environ=None):
        # Because we're no longer returning html, our content type is no
        # longer text/html
        # return [('Content-Type', 'text/plain')]
        headers = OrderedDict(super().get_headers(environ))
        headers['Content-Type'] = 'text/plain'
        return headers.items()


# The following exceptions are already implemented in werkzeug  Wrap them
# in our exception class so they don't return html
BadRequest = Base.wrap(exceptions.BadRequest)
Unauthorized = Base.wrap(exceptions.Unauthorized)
Forbidden = Base.wrap(exceptions.Forbidden)
NotFound = Base.wrap(exceptions.NotFound)
MethodNotAllowed = Base.wrap(exceptions.MethodNotAllowed)
NotAcceptable = Base.wrap(exceptions.NotAcceptable)
RequestTimeout = Base.wrap(exceptions.RequestTimeout)
Conflict = Base.wrap(exceptions.Conflict)
Gone = Base.wrap(exceptions.Gone)
LengthRequired = Base.wrap(exceptions.LengthRequired)
PreconditionFailed = Base.wrap(exceptions.PreconditionFailed)
RequestEntityTooLarge = Base.wrap(exceptions.RequestEntityTooLarge)
UnsupportedMediaType = Base.wrap(exceptions.UnsupportedMediaType)
ExpectationFailed = Base.wrap(exceptions.ExpectationFailed)
UnprocessableEntity = Base.wrap(exceptions.UnprocessableEntity)
InternalServerError = Base.wrap(exceptions.InternalServerError)
NotImplemented = Base.wrap(exceptions.NotImplemented)
BadGateway = Base.wrap(exceptions.BadGateway)
ServiceUnavailable = Base.wrap(exceptions.ServiceUnavailable)
RequestedRangeNotSatisfiable = Base.wrap(
    exceptions.RequestedRangeNotSatisfiable)


# The following exceptions are not already implemented in werkzeug and require
# that we create them ourselves.


class PaymentRequired(Base):  # 402
    code = client.PAYMENT_REQUIRED
    description = (
        'The server requires additional payment before '
        'this resource can be accessed.'
    )


class ProxyAuthenticationRequired(Base):  # 407
    code = client.PROXY_AUTHENTICATION_REQUIRED
    description = (
        'The proxy requires authentication before '
        'this resource can be accessed.'
    )


class RequestUriTooLong(Base):  # 414
    code = client.REQUEST_URI_TOO_LONG
    description = ('The uri used to access this resource is too long.')


class Locked(Base):  # 423
    code = client.LOCKED
    description = (
        'This resource is currently locked.  '
        'Please try again later.'
    )


class FailedDependency(Base):  # 424
    code = client.FAILED_DEPENDENCY
    description = (
        'A prior request is reqired as a dependency for this request.'
    )


class UgradeRequired(Base):  # 426
    code = client.UPGRADE_REQUIRED
    description = (
        'Client should re-attempt request using a different protocol.'
    )


class GatewayTimeout(Base):  # 504
    code = client.GATEWAY_TIMEOUT
    description = (
        'Gateway did not recieve a response from the upstream server.'
    )


class HttpVersionNotSupported(Base):  # 505
    code = client.HTTP_VERSION_NOT_SUPPORTED
    description = (
        'Server does not support the http protocol version used to connect.'
    )


class InsufficientStorage(Base):  # 507
    code = client.INSUFFICIENT_STORAGE
    description = (
        'Server has exceeded maximum storage capacity '
        'required to complete this request'
    )


class NotExtended(Base):
    code = client.NOT_EXTENDED
    description = (
        'Further extensions to the request are required'
        'for the server to fulfill it.'
    )
