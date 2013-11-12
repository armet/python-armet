# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
from .base import BaseResourceTest


class TestResourceValidation(BaseResourceTest):

    def test_post_too_low(self, connectors):
        data = {'votes': -14}
        body = json.dumps(data)
        response, content = self.client.post(
            path='/api/poll-valid/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert 'votes' in data
        assert data['votes'] == ['Must be greater than 0.']

    def test_post_too_high(self, connectors):
        data = {'votes': 54}
        body = json.dumps(data)
        response, content = self.client.post(
            path='/api/poll-valid/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert 'votes' in data
        assert data['votes'] == ['Must be less than 51.']

    def test_post_lots_wrong(self, connectors):
        data = {'votes': 0, 'question': 'This'}
        body = json.dumps(data)
        response, content = self.client.post(
            path='/api/poll-valid/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert 'votes' in data
        assert 'question' in data
        assert data['votes'][0] == 'Must be greater than 0.'
        assert data['question'][0] == 'Must be more than 15 characters.'
        assert data['question'][1] == 'Must have at least one question mark.'
