# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
from .base import BaseResourceTest
import pytest

# Shortcut to the skipif marker.
skipif = pytest.mark.skipif


class TestResourceAccess(BaseResourceTest):

    def test_simple(self, connectors):
        response, _ = self.client.get('/api/simple/')

        assert response.status == http.client.OK

    def test_redirect(self, connectors):
        response, _ = self.client.get('/api/simple')

        assert response.status == http.client.MOVED_PERMANENTLY

        uri = 'http://{}:{}/api/simple/'.format(self.host, self.port)
        assert response.get('location') == uri

    def test_redirect_trailing(self, connectors):
        response, _ = self.client.get('/api/simple-trailing/')

        assert response.status == http.client.MOVED_PERMANENTLY

        uri = 'http://{}:{}/api/simple-trailing'.format(self.host, self.port)
        assert response.get('location') == uri

    # NOTE: The below test fails in flask / werkzeug and I don't want
    #   to add crazy hacks to make it work.
    # <https://github.com/mitsuhiko/werkzeug/issues/402>
    # def test_redirect_complex(self, connectors):
    #     response, _ = self.client.get('/api/simple:hello(x=y)?x=3&y=4')

    #     assert response.status == http.client.MOVED_PERMANENTLY

    #     uri = 'http://{}:{}/api/simple:hello(x=y)/?x=3&y=4'.format(self.host,
    #                                                                self.port)
    #     assert response.get('location') == uri

    def test_not_found(self, connectors):
        response, _ = self.client.get('/api/unknown')

        assert response.status == http.client.NOT_FOUND

        response, _ = self.client.get('/api/unknown/')

        assert response.status == http.client.NOT_FOUND

    def test_unknown(self, connectors):
        response, _ = self.client.request('/api/simple/', method='APPLE')

        assert response.status == http.client.METHOD_NOT_ALLOWED

    def test_not_allowed(self, connectors):
        response, _ = self.client.request('/api/simple/', method='CONNECT')

        assert response.status == http.client.METHOD_NOT_ALLOWED

    def test_not_implemented(self, connectors):
        response, _ = self.client.request('/api/simple/', method='PATCH')

        assert response.status == http.client.NOT_IMPLEMENTED

    def test_streaming(self, connectors):
        response, content = self.client.request('/api/streaming/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'this\nwhere\nwhence\nthat\nwhy\nand the other'

    # @skipif("sys.version_info >= (3, 0)")
    # @skipif("__import__('platform').python_implementation() == 'PyPy'")
    # def test_async(self, connectors):
    #     response, content = self.client.request('/api/async/')
    #     data = content.decode('utf-8')

    #     assert response.status == 412
    #     assert response.get('content-type') == 'text/plain'
    #     assert data == 'Hello'

    # @skipif("sys.version_info >= (3, 0)")
    # @skipif("__import__('platform').python_implementation() == 'PyPy'")
    # def test_async_stream(self, connectors):
    #     response, content = self.client.request('/api/async-stream/')
    #     content = content.decode('utf-8')

    #     assert response.status == 412
    #     assert response.get('content-type') == 'text/plain'
    #     assert content == 'this\nwhere\nwhence\nthat\nwhy\nand the other'


class TestResourceLightweight(BaseResourceTest):

    def test_lightweight(self, connectors):
        response, content = self.client.get('/api/lightweight/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello'

    def test_lightweight_post(self, connectors):
        response, content = self.client.post('/api/lightweight/')
        data = content.decode('utf-8')

        assert response.status == 414
        assert response.get('content-type') == 'text/plain'
        assert data == 'Hello POST'

    def test_lightweight_streaming(self, connectors):
        response, content = self.client.request('/api/lightweight-streaming/')
        data = content.decode('utf-8')

        assert response.status == 412
        assert response.get('content-type') == 'text/plain'
        assert data == 'this\nwhere\nwhence\nthat\nwhy\nand the other'

    # @skipif("sys.version_info >= (3, 0)")
    # @skipif("__import__('platform').python_implementation() == 'PyPy'")
    # def test_lightweight_async(self, connectors):
    #     response, content = self.client.request('/api/lightweight-async/')
    #     data = content.decode('utf-8')

    #     assert response.status == 412
    #     assert response.get('content-type') == 'text/plain'
    #     assert data == 'Hello'


class TestResourceCookie(BaseResourceTest):

    def test_send_and_check(self, connectors):
        response, content = self.client.request(
            path='/api/cookie/',
            headers={'Cookie': 'blue=color'})

        data = content.decode('utf-8')

        assert response.status == 200
        assert response.get('content-type') == 'text/plain'
        assert data == 'color'
