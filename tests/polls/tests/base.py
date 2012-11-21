from django.utils import unittest
import json
from lxml import etree


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
        return self.assertEqual(response.status_code, 200)

    def assertHttpCreated(self, response):
        """
        Ensures the response is returning a HTTP 201.
        """
        return self.assertEqual(response.status_code, 201)

    def assertHttpAccepted(self, response):
        """
        Ensures the response is returning either a HTTP 202 or a HTTP 204.
        """
        return self.assertTrue(response.status_code in [202, 204])

    def assertHttpMultipleChoices(self, response):
        """
        Ensures the response is returning a HTTP 300.
        """
        return self.assertEqual(response.status_code, 300)

    def assertHttpSeeOther(self, response):
        """
        Ensures the response is returning a HTTP 303.
        """
        return self.assertEqual(response.status_code, 303)

    def assertHttpNotModified(self, response):
        """
        Ensures the response is returning a HTTP 304.
        """
        return self.assertEqual(response.status_code, 304)

    def assertHttpBadRequest(self, response):
        """
        Ensures the response is returning a HTTP 400.
        """
        return self.assertEqual(response.status_code, 400)

    def assertHttpUnauthorized(self, response):
        """
        Ensures the response is returning a HTTP 401.
        """
        return self.assertEqual(response.status_code, 401)

    def assertHttpForbidden(self, response):
        """
        Ensures the response is returning a HTTP 403.
        """
        return self.assertEqual(response.status_code, 403)

    def assertHttpNotFound(self, response):
        """
        Ensures the response is returning a HTTP 404.
        """
        return self.assertEqual(response.status_code, 404)

    def assertHttpMethodNotAllowed(self, response):
        """
        Ensures the response is returning a HTTP 405.
        """
        return self.assertEqual(response.status_code, 405)

    def assertHttpConflict(self, response):
        """
        Ensures the response is returning a HTTP 409.
        """
        return self.assertEqual(response.status_code, 409)

    def assertHttpGone(self, response):
        """
        Ensures the response is returning a HTTP 410.
        """
        return self.assertEqual(response.status_code, 410)

    def assertHttpTooManyRequests(self, response):
        """
        Ensures the response is returning a HTTP 429.
        """
        return self.assertEqual(response.status_code, 429)

    def assertHttpApplicationError(self, response):
        """
        Ensures the response is returning a HTTP 500.
        """
        return self.assertEqual(response.status_code, 500)

    def assertHttpNotImplemented(self, response):
        """
        Ensures the response is returning a HTTP 501.
        """
        return self.assertEqual(response.status_code, 501)

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
