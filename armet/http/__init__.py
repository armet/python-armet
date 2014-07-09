from werkzeug.wrappers import BaseRequest, BaseResponse, ResponseStreamMixin


class Request(BaseRequest):
    pass


class Response(BaseResponse, ResponseStreamMixin):
    pass
