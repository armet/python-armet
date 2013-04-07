# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import unittest
import json
from armet import encoders


class JsonEncoderTestCase(unittest.TestCase):

    def setUp(self):
        mime_type = 'application/json'
        self.encoder = encoders.JsonEncoder(mime_type, None)
        self.encode = self.encoder.encode

    def test_none(self):
        value = self.encode(None)

        self.assertEqual(value, '{}')

    def test_nothing(self):
        value = self.encode()

        self.assertEqual(value, '{}')

    def test_number(self):
        value = self.encode(42)

        self.assertEqual(value, '[42]')

    def test_boolean(self):
        value = self.encode(True)

        self.assertEqual(value, '[true]')

        value = self.encode(False)

        self.assertEqual(value, '[false]')

    def test_array(self):
        value = self.encode([1, 2, 3])

        self.assertEqual(value, '[1,2,3]')

    def test_array_nested(self):
        value = self.encode([1, [2, 4, 5], 3])

        self.assertEqual(value, '[1,[2,4,5],3]')

    def test_dict(self):
        message = {'x': 1, 'y': 2}
        value = self.encode(message)

        self.assertEqual(json.loads(value), message)
