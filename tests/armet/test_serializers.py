# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
import json
from armet import serializers, test
from armet.http import exceptions


class SerializerTestCase(unittest.TestCase):

    media_type = None

    Serializer = None

    @classmethod
    def setUpClass(cls):
        cls.response = test.http.Response()
        cls.request = None  # test.http.Request(...)
        cls.serializer = cls.Serializer(cls.request, cls.response)

    def serialize(self, data):
        self.response.clear()
        self.serializer.serialize(data)
        self.response.close()
        self.content = self.response.content.decode('utf-8')


class JSONSerializerTestCase(SerializerTestCase):

    media_type = 'application/json'

    Serializer = serializers.JSONSerializer

    def test_none(self):
        self.serialize(None)
        self.assertEqual(self.content, '{}')

    def test_number(self):
        self.serialize(42)
        self.assertEqual(self.content, '[42]')

    def test_boolean(self):
        self.serialize(True)
        self.assertEqual(self.content, '[true]')

        self.serialize(False)
        self.assertEqual(self.content, '[false]')

    def test_array(self):
        self.serialize([1, 2, 3])
        self.assertEqual(self.content, '[1,2,3]')

    def test_array_nested(self):
        self.serialize([1, [2, 4, 5], 3])
        self.assertEqual(self.content, '[1,[2,4,5],3]')

    def test_dict(self):
        message = {'x': 1, 'y': 2}
        self.serialize(message)
        self.assertEqual(json.loads(self.content), message)

    def test_generator(self):
        self.serialize(x for x in range(10))
        self.assertEqual(self.content, '[0,1,2,3,4,5,6,7,8,9]')


class URLSerializerTestCase(SerializerTestCase):

    media_type = 'application/x-www-form-urlencoded'

    Serializer = serializers.URLSerializer

    def test_none(self):
        self.serialize(None)
        self.assertEqual(self.content, '')

    def test_nested(self):
        self.serialize({"foo": [1, 2, 3]})
        self.assertEqual(self.content, 'foo=1&foo=2&foo=3')

    def test_impossible(self):
        req = [{"foo": "bar"}, {"bar": "baz"}]
        self.assertRaises(exceptions.NotAcceptable, self.serialize, req)

    def test_tuple(self):
        self.serialize([('foo', 'bar'), ('bar', 'baz')])
        expected = "foo=bar&bar=baz"
        self.assertEqual(self.content, expected)
