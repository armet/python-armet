# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import ujson as json
import six
import uuid
from armet import serializers
from pytest import mark, raises


class TestSerializer:

    media_type = None

    Serializer = None

    @classmethod
    def setup_class(cls):
        cls.serializer = cls.Serializer()

    def serialize(self, data):
        content = self.serializer.serialize(data)
        if content and isinstance(content, six.binary_type):
            content = content.decode('utf8')

        self.content = content


@mark.bench('self.serializer.serialize', iterations=10000)
class TestJSONSerializer(TestSerializer):

    media_type = 'application/json'

    Serializer = serializers.JSONSerializer

    def test_none(self):
        self.serialize(None)

        assert self.content == '{}'

    def test_number(self):
        self.serialize(42)

        assert self.content == '[42]'

    def test_boolean(self):
        self.serialize(True)

        assert self.content == '[true]'

        self.serialize(False)

        assert self.content == '[false]'

    def test_array(self):
        self.serialize([1, 2, 3])

        assert self.content == '[1,2,3]'

    def test_array_nested(self):
        self.serialize([1, [2, 4, 5], 3])

        assert self.content == '[1,[2,4,5],3]'

    def test_dict(self):
        message = {'x': 1, 'y': 2}
        self.serialize(message)

        assert json.loads(self.content) == message

    def test_generator(self):
        self.serialize(x for x in range(10))

        assert self.content == '[0,1,2,3,4,5,6,7,8,9]'

    def test_large(self):
        payload_item = {
            'organization': uuid.uuid4().hex,
            'user': uuid.uuid4().hex,
            'id': uuid.uuid4().hex,
            'is_active': False,
            'is_pending': True,
            'members': [
                {
                    'id': uuid.uuid4().hex,
                    'organization': uuid.uuid4().hex,
                    'is_dead': False
                }
            ],
        }

        payload = [payload_item] * 100

        self.serialize(payload)

        assert self.content == json.dumps(payload, ensure_ascii=False)


@mark.bench('self.serializer.serialize', iterations=10000)
class TestURLSerializer(TestSerializer):

    media_type = 'application/x-www-form-urlencoded'

    Serializer = serializers.URLSerializer

    def test_none(self):
        self.serialize(None)

        assert self.content == ''

    def test_nested(self):
        self.serialize({"foo": [1, 2, 3]})

        assert self.content == 'foo=1&foo=2&foo=3'

    def test_impossible(self):
        data = [{"foo": "bar"}, {"bar": "baz"}]
        with raises(ValueError):
            self.serialize(data)

    def test_tuple(self):
        self.serialize([('foo', 'bar'), ('bar', 'baz')])

        assert self.content == "foo=bar&bar=baz"
