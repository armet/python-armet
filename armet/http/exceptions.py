# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet.http import client


class BaseHTTPException(BaseException):
    status = None

    def __init__(self, content=None, headers=None):
        #! Body of the exception message.
        self.content = content

        #! Additional headers to place with the response.
        self.headers = headers or {}


class BadRequest(BaseHTTPException):  # 400
    status = client.BAD_REQUEST


class Unauthorized(BaseHTTPException):  # 401
    status = client.UNAUTHORIZED


class PaymentRequired(BaseHTTPException):  # 402
    status = client.PAYMENT_REQUIRED


class Forbidden(BaseHTTPException):  # 403
    status = client.FORBIDDEN


class NotFound(BaseHTTPException):  # 404
    status = client.NOT_FOUND


class MethodNotAllowed(BaseHTTPException):  # 405
    status = client.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        super(MethodNotAllowed, self).__init__(
            headers={'Allow': ', '.join(allowed)})


class NotAcceptable(BaseHTTPException):  # 406
    status = client.NOT_ACCEPTABLE


class ProxyAuthenticationRequired(BaseHTTPException):  # 407
    status = client.PROXY_AUTHENTICATION_REQUIRED


class RequestTimeout(BaseHTTPException):  # 408
    status = client.REQUEST_TIMEOUT


class Conflict(BaseHTTPException):  # 409
    status = client.CONFLICT


class Gone(BaseHTTPException):  # 410
    status = client.GONE


class LengthRequired(BaseHTTPException):  # 411
    status = client.LENGTH_REQUIRED


class PreconditionFailed(BaseHTTPException):  # 412
    status = client.PRECONDITION_FAILED


class RequestEntityTooLarge(BaseHTTPException):  # 413
    status = client.REQUEST_ENTITY_TOO_LARGE


class RequestUriTooLong(BaseHTTPException):  # 414
    status = client.REQUEST_URI_TOO_LONG


class UnsupportedMediaType(BaseHTTPException):  # 415
    status = client.UNSUPPORTED_MEDIA_TYPE


class RequestedRangeNotSatisfiable(BaseHTTPException):  # 416
    status = client.REQUESTED_RANGE_NOT_SATISFIABLE


class ExpectationFailed(BaseHTTPException):  # 417
    status = client.EXPECTATION_FAILED


class UnprocessableEntity(BaseHTTPException):  # 422
    status = client.UNPROCESSABLE_ENTITY


class Locked(BaseHTTPException):  # 423
    status = client.LOCKED


class FailedDependency(BaseHTTPException):  # 424
    status = client.FAILED_DEPENDENCY


class UgradeRequired(BaseHTTPException):  # 426
    status = client.UPGRADE_REQUIRED


class InternalServerError(BaseHTTPException):  # 500
    status = client.INTERNAL_SERVER_ERROR


class NotImplemented(BaseHTTPException):  # 501
    status = client.NOT_IMPLEMENTED


class BadGateway(BaseHTTPException):  # 502
    status = client.BAD_GATEWAY


class ServiceUnavailable(BaseHTTPException):  # 503
    status = client.SERVICE_UNAVAILABLE


class GatewayTimeout(BaseHTTPException):  # 504
    status = client.GATEWAY_TIMEOUT


class HttpVersionNotSupported(BaseHTTPException):  # 505
    status = client.HTTP_VERSION_NOT_SUPPORTED


class InsufficientStorage(BaseHTTPException):  # 507
    status = client.INSUFFICIENT_STORAGE


class NotExtended(BaseHTTPException):  # 510
    status = client.NOT_EXTENDED
