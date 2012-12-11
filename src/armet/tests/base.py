from django.utils import unittest
import json
from lxml import etree
from armet import http


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
        return self.assertEqual(response.status_code, http.client.OK)

    def assertHttpCreated(self, response):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(response.status_code, http.client.CREATED)

    def assertHttpAccepted(self, response):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertTrue(response.status_code in [http.client.ACCEPTED, http.client.NO_CONTENT])

    def assertHttpMultipleChoices(self, response):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(response.status_code, http.client.MULTIPLE_CHOICES)

    def assertHttpSeeOther(self, response):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(response.status_code, http.client.SEE_OTHER)

    def assertHttpNotModified(self, response):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(response.status_code, http.client.NOT_MODIFIED)

    def assertHttpBadRequest(self, response):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(response.status_code, http.client.BAD_REQUEST)

    def assertHttpUnauthorized(self, response):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(response.status_code, http.client.UNAUTHORIZED)

    def assertHttpForbidden(self, response):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(response.status_code, http.client.FORBIDDEN)

    def assertHttpNotFound(self, response):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(response.status_code, http.client.NOT_FOUND)

    def assertHttpMethodNotAllowed(self, response):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(response.status_code, http.client.METHOD_NOT_ALLOWED)

    def assertHttpNotAcceptable(self, response):
        """
        Ensures the response is returning a HTTP 406.
        """
        return self.assertEqual(response.status_code, http.client.NOT_ACCEPTABLE)

    def assertHttpConflict(self, response):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(response.status_code, http.client.CONFLICT)

    def assertHttpGone(self, response):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(response.status_code, http.client.GONE)

    def assertHttpTooManyRequests(self, response):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(response.status_code, http.client.TOO_MANY_REQUESTS)

    def assertHttpUnsupportedMediaType(self, response):
        """
        Ensures the response is returning a HTTP 415.
        """
        return self.assertEqual(response.status_code, http.client.UNSUPPORTED_MEDIA_TYPE)

    def assertHttpTeapot(self, response):
        """
        Ensures the response is returning a HTTP 418.
        """
        return self.assertEqual(response.status_code, http.client.TEAPOT)

    def assertHttpApplicationError(self, response):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(response.status_code, http.client.APPLICATION_ERROR)

    def assertHttpNotImplemented(self, response):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(response.status_code, http.client.NOT_IMPLEMENTED)

    def deserialize(self, response, type='json'):
        if type == 'json':
            try:
                return json.loads(response.content)
            except ValueError:
                return self.assertEqual(False, 'Invalid JSON format.')
        elif type == 'xml':
            try:
                content = etree.fromstring(response.content)
                return dict((x.get('name'), x.text)
                    for x in content.findall('attribute'))
            except etree.XMLSyntaxError:
                return self.assertEqual(False, 'Invalid XML format.')

    def assertValidJSONResponse(self, response):
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        return self.deserialize(response, type='json')
