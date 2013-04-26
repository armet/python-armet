# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import http, test


class AccessTestCase(test.TestCase):

    def test_access(self):
        response, _ = self.client.request('/api/simple/')

        self.assertEqual(response.status, http.client.OK)

    def test_redirect(self):
        response, _ = self.client.request('/api/simple')

        self.assertEqual(response.status, http.client.MOVED_PERMANENTLY)

        location = response.get('location')
        self.assertEqual(location, 'http://localhost:5000/api/simple/')

    def test_override(self):
        response, _ = self.client.request(
            '/api/simple/', 'PATCH', headers={
                'X-HTTP-Method-Override': 'GET'
            })

        self.assertEqual(response.status, http.client.OK)

    def test_http_whole_forbidden(self):
        response, _ = self.client.request(
            '/api/http-whole-forbidden/', 'POST')

        self.assertEqual(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_http_forbidden(self):
        response, _ = self.client.request('/api/http-forbidden/12/', 'DELETE')

        self.assertEqual(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_whole_forbidden(self):
        response, _ = self.client.request('/api/whole-forbidden/', 'POST')

        self.assertEqual(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_forbidden(self):
        response, _ = self.client.request('/api/forbidden/12/', 'DELETE')

        self.assertEqual(response.status, http.client.METHOD_NOT_ALLOWED)

    def test_redirect_slash(self):
        response, _ = self.client.request('/api/simple?foo=bar', 'POST')
        expected = 'http://localhost:5000/api/simple/?foo=bar'

        self.assertEqual(response.get('location'), expected)
