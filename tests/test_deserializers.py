# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
import uuid
from armet import deserializers
import ujson as json
from pytest import mark


class DeserializerTestCase(unittest.TestCase):

    Deserializer = None

    @classmethod
    def setup_class(cls):
        cls.deserializer = cls.Deserializer()

    def deserialize(self, text):
        self.data = self.deserializer.deserialize(text=text)


@mark.bench('self.deserialize', iterations=10000)
class JSONDeserializerTestCase(DeserializerTestCase):

    Deserializer = deserializers.JSONDeserializer

    def test_scalar(self):
        self.assertRaises(ValueError, self.deserialize, 124)

    def test_number(self):
        self.deserialize(b'[42]')

        assert self.data == [42]

    def test_boolean(self):
        self.deserialize(b'[true]')

        assert self.data == [True]

        self.deserialize(b'[false]')

        assert self.data == [False]

    def test_array(self):
        self.deserialize(b'[1, 2, 3]')

        assert self.data == [1, 2, 3]

    def test_dict(self):
        self.deserialize(b'{"x": 2, "y": "bob"}')

        assert self.data == {"x": 2, "y": "bob"}

    def test_dict_array(self):
        self.deserialize(b'{"x": [1, 2], "y": "bob"}')

        assert self.data == {"x": [1, 2], "y": "bob"}

    def test_large(self):
        payload_item = {
            'organization': uuid.uuid4().hex,
            'user': uuid.uuid4().hex,
            'id': uuid.uuid4().hex,
            'is_active': False,
            'is_pending': True,
            # 'members': [
            #     {
            #         'id': uuid.uuid4().hex,
            #         'organization': uuid.uuid4().hex,
            #         'is_dead': False
            #     }
            # ],
        }

        payload = [payload_item] * 100

        text = json.dumps(payload, ensure_ascii=False)

        self.deserialize(text.encode('utf8'))

        assert self.data == payload


@mark.bench('self.deserialize', iterations=10000)
class URLDeserializerTestCase(DeserializerTestCase):

    Deserializer = deserializers.URLDeserializer

    def test_scalar(self):
        self.assertRaises(ValueError, self.deserialize, 124)

    def test_sequence(self):
        self.deserialize(b'x=2&y=51')

        assert self.data == {'x': ['2'], 'y': ['51']}

    def test_multi_sequence(self):
        self.deserialize(b'x=2&y=51&x=781&y=165')

        assert self.data == {"x": ['2', '781'], "y": ['51', '165']}
