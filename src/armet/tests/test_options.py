# -*- coding: utf-8 -*-
from django.test.client import RequestFactory
from armet import http
from armet.resources import Resource
from armet.utils import test


class ChoiceEndPoint(Resource):
    http_allowed_methods = (
        'HEAD',
        'GET',
        'OPTIONS',
    )

    allowed_origins = ('http://127.0.0.1:80',)
    http_allowed_headers = ('Content-Type', 'Content-MD5', 'Accept')


class PollEndPoint(Resource):
    http_allowed_methods = (
        'HEAD',
        'GET',
        'DELETE',
        'OPTIONS',
    )

    allowed_origins = ('*',)
    http_allowed_headers = ('Content-Type', 'Content-MD5', 'Accept')


class OptionsMethodTestCase(test.TestCase):

    def setUp(self):
        super(OptionsMethodTestCase, self).setUp()
        self.choice_endpoint = '/choice'
        self.poll_endpoint = '/poll'
        self.choice_origin = 'http://127.0.0.1:80'
        self.poll_origin = 'http://10.0.0.1'
        self.default_method = 'GET'

    def test_origin_header(self):
        # Check an endpoint with a specific origin.
        # Try with no Origin request.
        # Should just send back 200.
        request = RequestFactory().options(self.choice_endpoint)
        response = ChoiceEndPoint.view(request)
        self.assertHttpStatus(response, http.client.OK)

        # Try with Origin not in the list of allowed origins.
        request = RequestFactory().options(self.choice_endpoint,
                                           ORIGIN=self.poll_origin)
        response = ChoiceEndPoint.view(request)
        self.assertHttpStatus(response, http.client.OK)

        # Try with the correct Origin.
        request = RequestFactory().options(self.choice_endpoint,
                                           ORIGIN=self.choice_origin)
        response = ChoiceEndPoint.view(request)
        self.assertHttpStatus(response, http.client.OK)

        # Check an endpoint which allows all origins.
        # Try with no Origin request.
        # Should just send back 200.
        request = RequestFactory().options(self.poll_endpoint)
        response = PollEndPoint.view(request)
        self.assertHttpStatus(response, http.client.OK)

        # Try with any random origin.
        request = RequestFactory().options(self.poll_endpoint,
                                           ORIGIN=self.poll_origin)
        response = PollEndPoint.view(request)
        self.assertHttpStatus(response, http.client.OK)

    def access_control_headers(self, header):
        """Test each Access-Control-Allow header here,
        since they all do the same thing.

        @param[in] header
            The header to test
        """

        # Check an endpoint that has a specific origin.
        # Check with no origin.
        request = RequestFactory().options(self.choice_endpoint)
        response = ChoiceEndPoint.view(request)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header(header))
        # Set the origin to the correct place.
        request = RequestFactory().options(self.choice_endpoint,
                                           ORIGIN=self.choice_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        response = ChoiceEndPoint.view(request)
        # Should give back a 200 and an Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header(header))
        # Do it again with asterisk.
        request = RequestFactory().options(self.choice_endpoint, ORIGIN='*')
        response = ChoiceEndPoint.view(request)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header(header))
        # Should probably check that we're getting the correct methods back.

        # Now try with an enpoint that allows any origin.
        # Check with no origin.
        request = RequestFactory().options(self.poll_endpoint)
        response = PollEndPoint.view(request)
        # Should give back a 200 and no Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertFalse(response.has_header(header))
        # Set the origin to the correct place.
        request = RequestFactory().options(self.poll_endpoint,
                ORIGIN=self.poll_origin,
                ACCESS_CONTROL_REQUEST_METHOD=self.default_method)
        response = PollEndPoint.view(request)
        # Should give back a 200 and an Allow-Headers header.
        self.assertHttpStatus(response, http.client.OK)
        self.assertTrue(response.has_header(header))
        # Should probably check that we're getting the correct methods back.

    def test_access_control_allow_headers(self):
        """Test the Access-Control-Allow-Headers header."""

        self.access_control_headers('Access-Control-Allow-Headers')

    def test_access_control_allow_methods(self):
        """Test the Access-Control-Allow-Methods header."""

        self.access_control_headers('Access-Control-Allow-Methods')

    def test_access_control_allow_origin(self):
        """Test the Access-Control-Allow-Origin header."""

        self.access_control_headers('Access-Control-Allow-Origin')
