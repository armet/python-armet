# -*- coding: utf-8 -*-
from armet import http
from armet.utils import test


class OptionsMethodTestCase(test.TestCase):

    def setUp(self):
        super(OptionsMethodTestCase, self).setUp()
        self.endpoint = '/'
        self.choice_origin = 'http://127.0.0.1:80'
        self.poll_origin = 'http://10.0.0.1'
        self.default_method = 'GET'

    def test_origin_header(self):
        # endpoint = '/'
        # Check an endpoint with a specific origin.
        endpoint = '{}choice'.format(self.endpoint)

        # Try with no Origin request.
        # Should just send back 200.
        response = self.client.options(endpoint)
        self.assertHttpStatus(response, http.client.OK)

        # Try with Origin not in the list of allowed origins.
        response = self.client.options(endpoint, ORIGIN=self.poll_origin)
        self.assertHttpStatus(response, http.client.OK)

        # Try with the correct Origin.
        response = self.client.options(endpoint, ORIGIN=self.choice_origin)
        self.assertHttpStatus(response, http.client.OK)

        # Check an endpoint which allows all origins.
        endpoint = '{}poll'.format(self.endpoint)

        # Try with no Origin request.
        # Should just send back 200.
        response = self.client.options(endpoint)
        self.assertHttpStatus(response, http.client.OK)

        # Try with any random origin.
        response = self.client.options(endpoint, ORIGIN=self.poll_origin)
        self.assertHttpStatus(response, http.client.OK)

    def test_access_control_allow_headers(self):
        # Check an endpoint that has a specific origin.
        endpoint = '{}choice'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Headers'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.choice_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Headers'))
        # Do it again with asterisk.
        asterisk = '*'
        response = self.client.options(endpoint, ORIGIN=asterisk)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Headers'))
        # Should probably check that we're getting the correct methods back.

        # Now try with an enpoint that allows any origin.
        endpoint = '{}poll'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Headers'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.poll_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Headers'))
        # Should probably check that we're getting the correct methods back.

    def test_access_control_allow_methods(self):
        # Check an endpoint that has a specific origin.
        endpoint = '{}choice'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Methods header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Methods'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.choice_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Methods header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Methods'))
        # Do it again with asterisk.
        asterisk = '*'
        response = self.client.options(endpoint, ORIGIN=asterisk)
        # Should give back a 200 and no Allow-Methods header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Methods'))
        # Should probably check that we're getting the correct methods back.

        # Now try with an enpoint that allows any origin.
        endpoint = '{}poll'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Methods header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Methods'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.poll_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Methods header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Methods'))
        # Should probably check that we're getting the correct methods back.

    def test_access_control_allow_origin(self):
        # Check an endpoint that has a specific origin.
        endpoint = '{}choice'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Origin header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Origin'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.choice_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Origin header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Origin'))
        # Assert we got the corrent origin back.
        self.assertEqual(response['Access-Control-Allow-Origin'],
                         self.choice_origin)
        # Do it again with asterisk.
        asterisk = '*'
        response = self.client.options(endpoint, ORIGIN=asterisk)
        # Should give back a 200 and no Allow-Origin header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Origin'))

        # Now try with an enpoint that allows any origin.
        endpoint = '{}poll'.format(self.endpoint)
        # Check with no origin.
        response = self.client.options(endpoint)
        # Should give back a 200 and no Allow-Origin header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header('Access-Control-Allow-Origin'))
        # Set the origin to the correct place.
        response = self.client.options(endpoint, ORIGIN=self.poll_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        # Should give back a 200 and an Allow-Origin header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Origin'))
