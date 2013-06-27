# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
import pytest
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

    @pytest.mark.skipif("sys.version_info >= (3, 0)")
    @pytest.mark.skipif("platform.python_implementation == 'PyPy'")
    def test_async(self, connectors):
        response, content = self.client.request('/api/async/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello'

    @pytest.mark.skipif("sys.version_info >= (3, 0)")
    @pytest.mark.skipif("platform.python_implementation == 'PyPy'")
    def test_async_stream(self, connectors):
        response, content = self.client.request('/api/async-stream/')
        content = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert content == 'this\nwhere\nwhence\nthat\nwhy\nand the other'

    def test_lightweight(self, connectors):
        response, content = self.client.get('/api/lightweight/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello'

    def test_lightweight_streaming(self, connectors):
        response, content = self.client.request('/api/lightweight-streaming/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'this\nwhere\nwhence\nthat\nwhy\nand the other'

    @pytest.mark.skipif("sys.version_info >= (3, 0)")
    @pytest.mark.skipif("platform.python_implementation == 'PyPy'")
    def test_lightweight_async(self, connectors):
        response, content = self.client.request('/api/lightweight-async/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello'
