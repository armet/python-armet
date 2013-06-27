# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
from .base import BaseResourceTest


class TestResourceAccess(BaseResourceTest):

    def test_simple(self, connectors):
        response, _ = self.client.get('/api/simple/')

        assert response.status == http.client.OK

    def test_redirect(self, connectors):
        response, _ = self.client.get('/api/simple')

        assert response.status == http.client.MOVED_PERMANENTLY

        uri = 'http://{}:{}/api/simple/'.format(self.host, self.port)
        assert response.get('location') == uri

    def test_redirect_complex(self, connectors):
        response, _ = self.client.get('/api/simple:hello(x=y)?x=3&y=4')

        assert response.status == http.client.MOVED_PERMANENTLY

        uri = 'http://{}:{}/api/simple:hello(x=y)/?x=3&y=4'.format(self.host,
                                                                   self.port)
        assert response.get('location') == uri

    def test_not_found(self, connectors):
        response, _ = self.client.get('/api/unknown')

        assert response.status == http.client.NOT_FOUND

        response, _ = self.client.get('/api/unknown/')

        assert response.status == http.client.NOT_FOUND

    def test_unknown(self, connectors):
        response, _ = self.client.request('/api/simple/', method='APPLE')

        assert response.status == http.client.NOT_IMPLEMENTED

    def test_not_allowed(self, connectors):
        response, _ = self.client.request('/api/simple/', method='CONNECT')

        assert response.status == http.client.METHOD_NOT_ALLOWED

    def test_not_implemented(self, connectors):
        response, _ = self.client.request('/api/simple/', method='PATCH')

        assert response.status == http.client.NOT_IMPLEMENTED
