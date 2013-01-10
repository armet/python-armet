# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http
from armet.utils import test
from armet.resources import Resource


class ForbiddenMethod(Resource):
    http_allowed_methods = ('DELETE',)


class ForbiddenOperation(Resource):
    allowed_operations = ('destroy',)


# class ForbiddenPartiallyPut(Resource):
#     allowed_operations = ('destroy',)


# class ForbiddenPut(Resource):
#     allowed_operations = ('destroy',)


class ForbiddenTestCase(test.TestCase):

    def test_forbidden_method(self):
        """Asserting that forbbiden methods return 405."""
        request = RequestFactory().get('/choice/1')
        response = ForbiddenMethod.view(request, slug=1)

        self.assertHttpStatus(response, http.client.METHOD_NOT_ALLOWED)

    def test_forbidden_operation(self):
        """Asserting that forbbiden operations return 405."""
        request = RequestFactory().get('/choice/1')
        response = ForbiddenOperation.view(request, slug=1)

        self.assertHttpStatus(response, http.client.METHOD_NOT_ALLOWED)

    # TODO: These tests below need to work once PUT is implemented

    # def test_forbidden_partial_put(self):
    #     """Asserting that a partially forbidden PUT should return 403."""
    #     request = RequestFactory().put('/choice/1')
    #     response = ForbiddenPartiallyPut.view(request, slug=1)

    #     self.assertHttpStatus(response, http.client.METHOD_NOT_ALLOWED)

    # def test_forbidden_put(self):
    #     """Asserting that a completely forbidden PUT should return 405."""
    #     request = RequestFactory().get('/choice/1')
    #     response = ForbiddenPut.view(request, slug=1)

    #     self.assertHttpStatus(response, http.client.METHOD_NOT_ALLOWED)
