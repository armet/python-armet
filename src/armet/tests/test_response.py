# -*- coding: utf-8 -*-
import hashlib
from armet.utils import test


class ResponseTestCase(test.TestCase):

    def setUp(self):
        super(ResponseTestCase, self).setUp()
        self.endpoint = '/'

    def test_content_md5(self):
        # Check some random endpoint
        endpoint = '{}choice/1'.format(self.endpoint)
        response = self.client.get(endpoint)
        # Assert we got a Content-MD5 header
        self.assertTrue(response.has_header('Content-MD5'))
        # Make an MD5 of the body.
        md5_body = hashlib.md5(response.content).hexdigest()
        # Assert the MD5 is correct.
        self.assertEqual(response['Content-MD5'], md5_body)
