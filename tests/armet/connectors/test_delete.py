# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http
from .base import BaseResourceTest


class TestResourceDelete(BaseResourceTest):

    def test_delete_existing(self, connectors):
        response, content = self.client.delete(
            path='/api/poll/1/',
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.NO_CONTENT
