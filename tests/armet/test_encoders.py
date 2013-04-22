# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import unittest
import json
from armet import encoders
from armet.test.http import Response as MockResponse


class JsonEncoderTestCase(unittest.TestCase):

    def setUp(self):
        mime_type = 'application/json'
        self.response = MockResponse()
        self.encoder = encoders.JsonEncoder(mime_type, None, self.response)
        self.encode = self.encoder.encode

    def test_none(self):
        self.response.reset()
        self.encode(None)
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '{}')

    def test_nothing(self):
        self.response.reset()
        self.encode()
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '{}')

    def test_number(self):
        self.response.reset()
        self.encode(42)
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[42]')

    def test_boolean(self):
        self.response.reset()
        self.encode(True)
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[true]')

        self.response.reset()
        self.encode(False)
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[false]')

    def test_array(self):
        self.response.reset()
        self.encode([1, 2, 3])
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[1,2,3]')

    def test_array_nested(self):
        self.response.reset()
        self.encode([1, [2, 4, 5], 3])
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[1,[2,4,5],3]')

    def test_dict(self):
        message = {'x': 1, 'y': 2}
        self.response.reset()
        self.encode(message)
        self.response.close()
        value = self.response.content

        self.assertEqual(json.loads(value), message)

    def test_generator(self):
        self.response.reset()
        self.encode(x for x in range(10))
        self.response.close()
        value = self.response.content

        self.assertEqual(value, '[0,1,2,3,4,5,6,7,8,9]')
