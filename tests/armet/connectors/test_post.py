# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http, serializers, deserializers
from .base import BaseResourceTest


class TestResourceEcho(BaseResourceTest):

    @classmethod
    def setup_class(cls):
        super(TestResourceEcho, cls).setup_class()

        cls.body = {'x': ['1', '2', '3'], 'y': ['4', '5']}

        cls.serializers = {}
        cls.serializers['json'] = serializers.JSONSerializer()
        cls.serializers['url'] = serializers.URLSerializer()

        cls.deserializers = {}
        cls.deserializers['json'] = deserializers.JSONDeserializer()
        cls.deserializers['url'] = deserializers.URLDeserializer()

    def echo(self, in_format, out_format):
        body = self.serializers[in_format].serialize(self.body)
        response, content = self.client.post(
            path='/api/echo/', body=body,
            headers={
                'Content-Type': self.serializers[in_format].media_types[0],
                'Accept': self.serializers[out_format].media_types[0]})

        assert response.status == http.client.OK

        data = self.deserializers[out_format].deserialize(content)

        assert data == self.body

    def test_echo_json_json(self, connectors):
        self.echo('json', 'json')

    def test_echo_json_url(self, connectors):
        self.echo('json', 'url')

    def test_echo_url_url(self, connectors):
        self.echo('url', 'url')

    def test_echo_url_json(self, connectors):
        self.echo('url', 'json')
