# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import unittest
import json
from armet import encoders, http


# TODO: Move this to somewhere interesting like `armet.test.mock.Response`
class MockResponse(http.Response):

    def __init__(self, *args, **kwargs):
        super(MockResponse, self).__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.content = ''
        self.headers = {}
        self._status = 200

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def write(self, value):
        self.content += value

    def __getitem__(self, name):
        return self.headers[name]

    def __setitem__(self, name, value):
        self.headers[name] = value

    def __delitem__(self, name):
        del self.headers[str(name)]

    def __contains__(self, name):
        return name in self.headers

    def __iter__(self):
        return iter(self.headers)

    def __len__(self):
        return len(self.headers)


class JsonEncoderTestCase(unittest.TestCase):

    def setUp(self):
        mime_type = 'application/json'
        self.response = MockResponse()
        self.encoder = encoders.JsonEncoder(mime_type, None, self.response)
        self.encode = self.encoder.encode

    def test_none(self):
        self.response.reset()
        self.encode(None)
        value = self.response.content

        self.assertEqual(value, '{}')

    def test_nothing(self):
        self.response.reset()
        self.encode()
        value = self.response.content

        self.assertEqual(value, '{}')

    def test_number(self):
        self.response.reset()
        self.encode(42)
        value = self.response.content

        self.assertEqual(value, '[42]')

    def test_boolean(self):
        self.response.reset()
        self.encode(True)
        value = self.response.content

        self.assertEqual(value, '[true]')

        self.response.reset()
        self.encode(False)
        value = self.response.content

        self.assertEqual(value, '[false]')

    def test_array(self):
        self.response.reset()
        self.encode([1, 2, 3])
        value = self.response.content

        self.assertEqual(value, '[1,2,3]')

    def test_array_nested(self):
        self.response.reset()
        self.encode([1, [2, 4, 5], 3])
        value = self.response.content

        self.assertEqual(value, '[1,[2,4,5],3]')

    def test_dict(self):
        message = {'x': 1, 'y': 2}
        self.response.reset()
        self.encode(message)
        value = self.response.content

        self.assertEqual(json.loads(value), message)

    def test_generator(self):
        self.response.reset()
        self.encode(x for x in range(10))
        value = self.response.content

        self.assertEqual(value, '[0,1,2,3,4,5,6,7,8,9]')
