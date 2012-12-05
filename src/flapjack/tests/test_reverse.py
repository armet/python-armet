# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.utils import unittest
from django.test.client import RequestFactory
from flapjack import resources
from . import api


class ReverseTestCase(unittest.TestCase):

    def test_simple(self):
        request = RequestFactory().get('/')
        resource = api.Apple(request, slug=None, format=None)
        # resource.name = 'apple'

        self.assertEqual(resource.uri, '/apple')
