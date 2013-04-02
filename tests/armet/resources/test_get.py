# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from armet import http, test


class GetTestCase(test.TestCase):

    def test_access(self):
        response, _ = self.client.request('/api/poll/')

        self.assertEquals(response.status, http.client.OK)

    def test_redirect(self):
        response, _ = self.client.request('/api/poll')

        self.assertEquals(response.status, http.client.MOVED_PERMANENTLY)

        location = response.get('location')
        self.assertEquals(location, 'http://localhost:5000/api/poll/')

    def test_http_whole_forbidden(self):
        response, _ = self.client.request(
            '/api/http-whole-forbidden/', 'POST')

        self.assertEquals(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_http_forbidden(self):
        response, _ = self.client.request('/api/http-forbidden/12/', 'DELETE')

        self.assertEquals(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_whole_forbidden(self):
        response, _ = self.client.request('/api/whole-forbidden/', 'POST')

        self.assertEquals(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_forbidden(self):
        response, _ = self.client.request('/api/forbidden/12/', 'DELETE')

        self.assertEquals(response.status, http.client.METHOD_NOT_ALLOWED)
