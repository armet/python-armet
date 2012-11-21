from django.utils import unittest
import json
from lxml import etree
from flapjack.http.constants import *


class BaseTest(unittest.TestCase):
    """Unit Tests for Invitation related API calls"""

    fixtures = ['initial_data']

    def setUp(self):
        """Sets up a user and HTTP Django test clients
        """
        super(BaseTest, self).setUp()

    def tearDown(self):
        """
        Cleans up the user object
        """
        super(BaseTest, self).tearDown()

    def assertValidJSON(self, response):
        """
        Ensures the response is valid JSON
        """
        return self.deserialize(response, type='json')

    def assertValidXML(self, response):
        """
        Ensures the response is valid JSON
        """
        return self.deserialize(response, type='xml')

    def assertHttpOK(self, response):
        """
        Ensures the response is returning a HTTP 200.
        """
        return self.assertEqual(response.status_code, OK)

    def assertHttpCreated(self, response):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(response.status_code, CREATED)

    def assertHttpAccepted(self, response):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertTrue(response.status_code in [ACCEPTED, NO_CONTENT])

    def assertHttpMultipleChoices(self, response):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(response.status_code, MULTIPLE_CHOICES)

    def assertHttpSeeOther(self, response):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(response.status_code, SEE_OTHER)

    def assertHttpNotModified(self, response):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(response.status_code, NOT_MODIFIED)

    def assertHttpBadRequest(self, response):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(response.status_code, BAD_REQUEST)

    def assertHttpUnauthorized(self, response):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(response.status_code, UNAUTHORIZED)

    def assertHttpForbidden(self, response):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(response.status_code, FORBIDDEN)

    def assertHttpNotFound(self, response):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(response.status_code, NOT_FOUND)

    def assertHttpMethodNotAllowed(self, response):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(response.status_code, METHOD_NOT_ALLOWED)

    def assertHttpNotAcceptable(self, response):
        """
        Ensures the response is returning a HTTP 406.
        """
        return self.assertEqual(response.status_code, NOT_ACCEPTABLE)

    def assertHttpConflict(self, response):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(response.status_code, CONFLICT)

    def assertHttpGone(self, response):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(response.status_code, GONE)

    def assertHttpTooManyRequests(self, response):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(response.status_code, TOO_MANY_REQUESTS)

    def assertHttpUnsupportedMediaType(self, response):
        """
        Ensures the response is returning a HTTP 415.
        """
        return self.assertEqual(response.status_code, UNSUPPORTED_MEDIA_TYPE)

    def assertHttpApplicationError(self, response):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(response.status_code, APPLICATION_ERROR)

    def assertHttpNotImplemented(self, response):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(response.status_code, NOT_IMPLEMENTED)

    def deserialize(self, response, type='json'):
        if type == 'json':
            try:
                content = json.loads(response.content)
            except ValueError:
                return self.assertEqual(False, 'Invalid JSON format.')
            return content
        elif type == 'xml':
            try:
                content = etree.fromstring(response.content)
            except etree.XMLSyntaxError:
                return self.assertEqual(False, 'Invalid XML format.')
            content = etree.fromstring(response.content)
            return dict((x.get('name'), x.text)
                for x in content.findall('attribute'))


# class Serializer():
