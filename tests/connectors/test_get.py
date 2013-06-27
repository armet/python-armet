# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
from .base import BaseResourceTest


class TestResourceGet(BaseResourceTest):

    def test_list(self):
        response, content = self.client.request('/api/poll/')

        content = json.loads(content.decode('utf-8'))

        assert response.status == http.client.OK
        assert isinstance(content, list)
        assert len(content) == 100
        assert content[0]['question'] == 'Are you an innie or an outie?'
        assert (content[-1]['question'] ==
                'What one question would you add to this survey?')

    def test_not_found(self, connectors):
        response, _ = self.client.get('/api/poll/101/')

        assert response.status == http.client.NOT_FOUND
