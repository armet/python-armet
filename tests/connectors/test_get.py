# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
import unittest
import six
from sys import platform
from .base import BaseResourceTest


class TestResourceGet(BaseResourceTest):

    def test_list(self):
        response, content = self.client.request('/api/poll/')
        data = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(data, list)
        assert len(data) == 100
        assert data[0]['question'] == 'Are you an innie or an outie?'
        assert (data[-1]['question'] ==
                'What one question would you add to this survey?')

    def test_not_found(self, connectors):
        response, _ = self.client.get('/api/poll/101/')

        assert response.status == http.client.NOT_FOUND

    def test_single(self, connectors):
        response, content = self.client.request('/api/poll/1/')
        data = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(data, dict)
        assert data['question'] == 'Are you an innie or an outie?'

        response, content = self.client.request('/api/poll/100/')
        data = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(data, dict)
        assert (data['question'] ==
                'What one question would you add to this survey?')

    def test_streaming(self, connectors):
        response, content = self.client.request('/api/streaming/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'this\nwhere\nwhence\nthat\nwhy\nand the other'

    def test_async(self, connectors):
        if six.PY3 and platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest('gevent not available for this platform')

        response, content = self.client.request('/api/async/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello'

    def test_async_stream(self, connectors):
        if six.PY3 and platform.python_implementation() == 'PyPy':
            raise unittest.SkipTest('gevent not available for this platform')

        response, content = self.client.request('/api/async-stream/')
        content = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert content == 'this\nwhere\nwhence\nthat\nwhy\nand the other'
