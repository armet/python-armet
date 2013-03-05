# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import itertools
import json
import msgpack
import six
import collections
from django.utils import unittest
from armet import encoders
from datetime import datetime


class JsonTestCase(unittest.TestCase):

    def setUp(self):
        self.json = encoders.Json()
        self.message = {
            'this': 'should',
            'that': 42,
            'bool': False,
            'list': [
                {'item': 'something', 'value': 'else'},
                {'item': 'something', 'value': 'else'},
                {'item': 'something', 'value': 'else'},
                {'item': 'something', 'value': 'else'},
            ]
        }

    def test_json_none(self):
        encoded = self.json.encode(None)
        content = json.loads(encoded)

        self.assertEqual(content, {})

    def test_json_complex(self):
        encoded = self.json.encode(complex(16, 12))
        content = json.loads(encoded)

        self.assertEqual(content[0], '16+12i')

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


class MessagePackTestCase(unittest.TestCase):

    def setUp(self):
        self.msgpack = encoders.Bin()
        self.message = {
            'this': 'should',
            'be': True,
            'completely': None,
            'replicatable': (
                'using',
                'loads',
                {
                    'float': 3.14,
                },
            ),
        }

    def stringify(self, thing):
        """because of the python2 unicode_literals backport, we must
        re-stringify all strings that come through msgpack.  This will be fixed
        with python3
        """
        if isinstance(thing, six.string_types):
            return str(thing)
        if isinstance(thing, collections.Mapping):
            fn = self.stringify
            return {fn(key): fn(value) for key, value in thing.iteritems()}
        if isinstance(thing, collections.Sequence):
            return tuple(self.stringify(item) for item in thing)
        return thing

    def test_common(self):
        encoded = self.msgpack.encode(self.message)
        decoded = msgpack.loads(encoded)

        # Stringify it for unicode_literals
        stringified = self.stringify(self.message)

        self.assertEqual(decoded, stringified)

    def test_date(self):
        date = datetime.now()
        decoded = msgpack.loads(self.msgpack.encode(date))

        self.assertEqual(decoded, date.isoformat())
