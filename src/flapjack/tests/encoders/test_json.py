# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import itertools
from django.utils import unittest
from flapjack import encoders
import json
import copy


class JsonEncoderTestCase(unittest.TestCase):

    def setUp(self):
        self.json = encoders.Json()
        self.message = {
            'this': 'should',
            'that': 42,
            'bool': False,
            'list': [
                { 'item': 'something', 'value': 'else' },
                { 'item': 'something', 'value': 'else' },
                { 'item': 'something', 'value': 'else' },
                { 'item': 'something', 'value': 'else' },
            ]
        }

    def test_json_none(self):
        encoded = self.json.encode(None)
        content = json.loads(encoded)

        self.assertEqual(content, {})

    def test_json_bool(self):
        encoded = self.json.encode(False)
        content = json.loads(encoded)

        self.assertEqual(content, [False])

    def test_json_dict(self):
        encoded = self.json.encode(self.message)
        content = json.loads(encoded)

        self.assertEqual(content, self.message)

    def test_json_list(self):
        message = [self.message for x in range(10)]
        encoded = self.json.encode(message)
        content = json.loads(encoded)

        self.assertEqual(content, message)

    def test_json_generator(self):
        message, save = itertools.tee((self.message for x in range(10)))
        encoded = self.json.encode(message)
        content = json.loads(encoded)

        self.assertEqual(content, list(save))

    def test_json_object(self):
        encoded = self.json.encode(type(b'message', (), self.message))
        content = json.loads(encoded)

        self.assertEqual(content, self.message)
