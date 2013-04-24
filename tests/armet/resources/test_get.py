# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http, test
import json
import platform
import six


class GetTestCase(test.TestCase):

    def test_list(self):
        response, content = self.client.request('/api/poll/')

        content = json.loads(content.decode('utf-8'))

        self.assertEqual(response.status, http.client.OK)
        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 100)
        self.assertEqual(
            content[0]['question'], 'Are you an innie or an outie?')
        self.assertEqual(
            content[-1]['question'],
            'What one question would you add to this survey?')

    def test_single(self):
        response, content = self.client.request('/api/poll/1/')

        content = json.loads(content.decode('utf-8'))

        self.assertEqual(response.status, http.client.OK)
        self.assertIsInstance(content, dict)
        self.assertEqual(
            content['question'], 'Are you an innie or an outie?')

        response, content = self.client.request('/api/poll/100/')

        content = json.loads(content.decode('utf-8'))

        self.assertEqual(response.status, http.client.OK)
        self.assertIsInstance(content, dict)
        self.assertEqual(
            content['question'],
            'What one question would you add to this survey?')

    def test_not_found(self):
        response, _ = self.client.request('/api/poll/101/')

        self.assertEqual(response.status, http.client.NOT_FOUND)

    def test_streaming(self):
        response, content = self.client.request('/api/streaming/')

        self.assertEqual(response.status, 202)
        self.assertEqual(response.get('content-type'), 'text/plain')
        self.assertEqual(
            content, 'this\nwhere\nwhence\nthat\nwhy\nand the other')

    def test_async(self):
        if six.PY3 or platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest('gevent not available for this platform')

        response, content = self.client.request('/api/async/')

        self.assertEqual(response.status, 202)
        self.assertEqual(response.get('content-type'), 'text/plain')
        self.assertEqual(content, 'Hello')

    def test_async_stream(self):
        if six.PY3 or platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest('gevent not available for this platform')

        response, content = self.client.request('/api/async-stream/')

        self.assertEqual(response.status, 202)
        self.assertEqual(response.get('content-type'), 'text/plain')
        self.assertEqual(
            content, 'this\nwhere\nwhence\nthat\nwhy\nand the other')
