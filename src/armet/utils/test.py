# -*- coding: utf-8 -*-
"""
Implementation of a test case with convenience assertions and facilities
easing the unit testing of RESTful APIs.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
from django.utils import unittest
from django.core import management
from django.test import client
from .. import http


class TestCase(unittest.TestCase):

    def setUp(self):
        #! A web service client for making requests.
        self.client = client.Client()

    def assertHttpStatus(self, response, *codes):
        # Iterable of status codes; check if we're in.
        self.assertIn(response.status_code, codes)

    def assertResponse(self, response, format='json', status=http.client.OK):
        # Assert the status codes first.
        self.assertHttpStatus(response, status)

        # TODO: Attempt to decode...
