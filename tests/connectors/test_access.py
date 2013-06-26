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

        location = response.get('location')
        assert location == 'http://{}:{}/api/simple/'.format(
            self.host, self.port)
