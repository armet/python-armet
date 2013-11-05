# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import json
from armet import http
from .base import BaseResourceTest


class TestResourceAttributeProperties(BaseResourceTest):

    def test_not_include(self):
        response, content = self.client.get('/api/poll-exclude/1/')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert 'id' in data
        assert 'question' not in data

    def test_not_include_access(self):
        response, content = self.client.get('/api/poll-exclude/1/question/')

        assert response.status == http.client.OK
        assert content.decode('utf8') == '["Are you an innie or an outie?"]'

    def test_not_read(self):
        response, content = self.client.get('/api/poll-unread/1/question/')

        assert response.status == http.client.FORBIDDEN

    def test_not_include_but_create(self):
        data = {'question': 'Is anybody really out there?'}
        body = json.dumps(data)
        response, content = self.client.post(
            path='/api/poll-exclude/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.CREATED

        data = json.loads(content.decode('utf8'))

        assert 'question' not in data
        assert data['id'] == 101

        response, content = self.client.get('/api/poll/101/')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert data['question'] == 'Is anybody really out there?'

    def test_not_include_but_replace(self):
        data = {'id': 1, 'question': 'Is anybody really out there?'}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-exclude/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert 'question' not in data
        assert data['id'] == 1

        response, content = self.client.get('/api/poll/1/')

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert data['question'] == 'Is anybody really out there?'

    def test_not_write(self):
        data = {'id': 123, 'question': 'gr9uer0gn2w'}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-unwrite/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert data['question'] == ['Attribute is read-only.']

    def test_not_write_same(self):
        data = {'id': 1, 'question': 'Is anybody really out there?'}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-unwrite/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.OK

    def test_no_null(self):
        data = {'question': None}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-no-null/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert data['question'] == ['Must not be null.']

    def test_required(self):
        data = {}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-required/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.BAD_REQUEST

        data = json.loads(content.decode('utf8'))

        assert data['question'] == ['Must be provided.']

    def test_name(self):
        data = {'superQuestion': 'something', 'id': 1}
        body = json.dumps(data)
        response, content = self.client.put(
            path='/api/poll-named/1/', body=body,
            headers={'Content-Type': 'application/json'})

        assert response.status == http.client.OK

        data = json.loads(content.decode('utf8'))

        assert 'superQuestion' in data
        assert data['superQuestion'] == 'something'
