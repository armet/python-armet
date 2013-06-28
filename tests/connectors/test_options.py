# -*- coding: utf-8 -*-
from armet import http
from .base import BaseResourceTest


class TestResourceOptions(BaseResourceTest):

    @classmethod
    def setup_class(cls):
        super(TestResourceOptions, cls).setup_class()
        cls.right_path = '/api/left/'
        cls.left_path = '/api/right/'
        cls.right_origin = 'http://127.0.0.1:80'
        cls.left_origin = 'http://10.0.0.1'
        cls.default_method = 'GET'

    def test_origin_header(self, connectors):
        # Check an endpoint with a specific origin.
        # Try with no Origin request.
        # Should just send back 200.
        response, _ = self.client.options(self.right_path)

        assert response.status == http.client.OK

        # Try with Origin not in the list of allowed origins.
        response, _ = self.client.options(
            self.right_path,
            headers={'Origin': self.left_origin})

        assert response.status == http.client.OK

        # Try with the correct Origin.
        response, _ = self.client.options(
            self.right_path,
            headers={'Origin': self.right_origin})

        assert response.status == http.client.OK

        # Check an endpoint which allows all origins.
        # Try with no Origin request.
        # Should just send back 200.
        response, _ = self.client.options(self.left_path)

        assert response.status == http.client.OK

        # Try with any random origin.
        response, _ = self.client.options(
            self.left_path,
            headers={'Origin': self.left_origin})

        assert response.status == http.client.OK

    def access_control_headers(self, header):
        """
        Test each Access-Control-Allow header here, since they
        all do the same thing.
        """

        # Check an endpoint that has a specific origin.
        # Check with no origin.
        response, _ = self.client.options(self.right_path)

        # Should give back a 200 and no Allow-Headers header.
        assert response.status == http.client.OK
        assert header not in response

        # Set the origin to the correct place.
        response, _ = self.client.options(
            self.right_path,
            headers={
                'Origin': self.right_origin,
                'Access-Control-Request-Method': self.default_method})

        # Should give back a 200 and an Allow-Headers header.
        assert response.status == http.client.OK
        assert header not in response

        # Do it again with asterisk.
        response, _ = self.client.options(
            self.right_path, headers={'Origin': '*'})

        # Should give back a 200 and no Allow-Headers header.
        assert response.status == http.client.OK
        assert header not in response

        # TODO: Should probably check that we're getting the
        #       correct methods back.

        # Now try with an enpoint that allows any origin.
        # Check with no origin.
        response, _ = self.client.options(self.left_path)

        # Should give back a 200 and no Allow-Headers header.
        assert response.status == http.client.OK
        assert header not in response

        # Set the origin to the correct place.
        response, _ = self.client.options(
            self.left_path,
            headers={
                'Origin': self.left_origin,
                'Access-Control-Request-Method': self.default_method})

        # Should give back a 200 and no Allow-Headers header.
        assert response.status == http.client.OK
        assert header not in response

        # Should probably check that we're getting the correct methods back.

    def test_access_control_allow_headers(self, connectors):
        """Test the Access-Control-Allow-Headers header."""
        self.access_control_headers('Access-Control-Allow-Headers')

    def test_access_control_allow_methods(self, connectors):
        """Test the Access-Control-Allow-Methods header."""
        self.access_control_headers('Access-Control-Allow-Methods')

    def test_access_control_allow_origin(self, connectors):
        """Test the Access-Control-Allow-Origin header."""
        self.access_control_headers('Access-Control-Allow-Origin')
