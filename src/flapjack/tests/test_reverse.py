# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.test import TestCase
from django.test.client import RequestFactory
from . import api


class ReverseTestCase(TestCase):

    def test_list(self):
        request = RequestFactory().get('/poll')
        resource = api.Poll(request)

        self.assertEqual(resource.uri, '/poll')

    def test_slug(self):
        request = RequestFactory().get('/poll/1')
        resource = api.Poll(request)

        self.assertEqual(resource.slug, '1')
        self.assertEqual(resource.uri, '/poll/1')

    def test_slug_long(self):
        slug = '1239853297572983'
        request = RequestFactory().get('/poll/{}'.format(slug))
        resource = api.Poll(request)

        self.assertEqual(resource.slug, slug)
        self.assertEqual(resource.uri, '/poll/{}'.format(slug))

    # TODO: test_attribute
    # TODO: test_local
    # TODO: test_local_many
