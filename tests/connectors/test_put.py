# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
from .base import BaseResourceTest


class TestResourcePut(BaseResourceTest):

    def test_put_existing(self, connectors):
        data = {'id': 1, 'question': 'Is anybody really out there?'}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert isinstance(data, dict)
        assert data['question'] == 'Is anybody really out there?'
        assert data['id'] == 1

    def test_put_nonexistant(self):
        request_data = {'id': 101, 'question': 'Is there anybody home?'}
        body = json.dumps(request_data)
        response, content = self.client.put(
            path='/api/poll/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert isinstance(data, dict)
        assert set(request_data.items()) <= set(data.items())
