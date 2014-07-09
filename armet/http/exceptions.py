from http import client


class Base(BaseException):
    status = None

    def __init__(self, content=None, headers=None):
        #! Body of the exception message.
        self.content = content

        #! Additional headers to place with the response.
        self.headers = headers or {}


class BadRequest(Base):  # 400
    status = client.BAD_REQUEST


class Unauthorized(Base):  # 401
    status = client.UNAUTHORIZED


class PaymentRequired(Base):  # 402
    status = client.PAYMENT_REQUIRED


class Forbidden(Base):  # 403
    status = client.FORBIDDEN


class NotFound(Base):  # 404
    status = client.NOT_FOUND


class MethodNotAllowed(Base):  # 405
    status = client.METHOD_NOT_ALLOWED

    def __init__(self, allowed):
        super(MethodNotAllowed, self).__init__(
            headers={'Allow': ', '.join(allowed)})


class NotAcceptable(Base):  # 406
    status = client.NOT_ACCEPTABLE


class ProxyAuthenticationRequired(Base):  # 407
    status = client.PROXY_AUTHENTICATION_REQUIRED


class RequestTimeout(Base):  # 408
    status = client.REQUEST_TIMEOUT


class Conflict(Base):  # 409
    status = client.CONFLICT


class Gone(Base):  # 410
    status = client.GONE


class LengthRequired(Base):  # 411
    status = client.LENGTH_REQUIRED


class PreconditionFailed(Base):  # 412
    status = client.PRECONDITION_FAILED


class RequestEntityTooLarge(Base):  # 413
    status = client.REQUEST_ENTITY_TOO_LARGE


class RequestUriTooLong(Base):  # 414
    status = client.REQUEST_URI_TOO_LONG


class UnsupportedMediaType(Base):  # 415
    status = client.UNSUPPORTED_MEDIA_TYPE


class RequestedRangeNotSatisfiable(Base):  # 416
    status = client.REQUESTED_RANGE_NOT_SATISFIABLE


class ExpectationFailed(Base):  # 417
    status = client.EXPECTATION_FAILED


class UnprocessableEntity(Base):  # 422
    status = client.UNPROCESSABLE_ENTITY


class Locked(Base):  # 423
    status = client.LOCKED


class FailedDependency(Base):  # 424
    status = client.FAILED_DEPENDENCY


class UgradeRequired(Base):  # 426
    status = client.UPGRADE_REQUIRED


class InternalServerError(Base):  # 500
    status = client.INTERNAL_SERVER_ERROR


class NotImplemented(Base):  # 501
    status = client.NOT_IMPLEMENTED


class BadGateway(Base):  # 502
    status = client.BAD_GATEWAY


class ServiceUnavailable(Base):  # 503
    status = client.SERVICE_UNAVAILABLE


class GatewayTimeout(Base):  # 504
    status = client.GATEWAY_TIMEOUT


class HttpVersionNotSupported(Base):  # 505
    status = client.HTTP_VERSION_NOT_SUPPORTED


class InsufficientStorage(Base):  # 507
    status = client.INSUFFICIENT_STORAGE


class NotExtended(Base):  # 510
    status = client.NOT_EXTENDED
