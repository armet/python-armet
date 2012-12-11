# -*- coding: utf-8 -*-
"""
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
from django.utils import unittest
from django.core import management
from django.test import client
# from lxml import etree
# import json
from .. import http


class Client(client.Client):

    def get(self, path, *args, **kwargs):
        return super(Client, self).get(path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return super(Client, self).post(path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        return super(Client, self).put(path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return super(Client, self).delete(path, *args, **kwargs)


class TestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def assertHttpStatus(self, response, code_or_codes):
        if isinstance(code_or_codes, collections.Iterable):
            # Iterable of status codes; check if we're in
            self.assertIn(response.status_code, code_or_codes)

        else:
            # Singular HTTP status code; check for it
            self.assertEqual(response.status_code, code_or_codes)

    def assertResponse(self, response, format='json', status=http.client.OK):
        # Assert the status codes first
        self.assertHttpStatus(response, status)

        # TODO: Attempt to decode
