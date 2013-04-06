# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import utils
from armet.http import request, response


class Request(request.Request):
    """Implements the request abstraction for cyclone.
    """

    @property
    @utils.memoize_single
    def method(self):
        pass

    def __getitem__(self):
        pass

    def __iter__(self):
        pass

    def __len__(self):
        pass


class Response(response.Response):
    """Implements the response abstraction for cyclone.
    """
