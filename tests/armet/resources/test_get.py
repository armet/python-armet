# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import test
import json


class GetTestCase(test.TestCase):

    def test_list(self):
        response, content = self.client.request('/api/poll/')

        content = json.loads(content)

        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 100)
        self.assertEqual(content[0]['question'],
            'Are you an innie or an outie?')
        self.assertEqual(content[-1]['question'],
            'What one question would you add to this survey?')
