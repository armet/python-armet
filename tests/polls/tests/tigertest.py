from tastypie.test import ResourceTestCase
from django.utils import unittest
from django.test.client import Client

class TigerTest(ResourceTestCase):
    """Unit Tests for the Are You A Tiger poll object"""

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_list_view_xml(self):
        """Gets the list view in xml format"""
        self.response = self.c.get('/api/v1/poll.xml/')
        self.assertEqual(self.response.status_code, 200)

    def test_list_view_json(self):
        """Gets the list view in json format"""
        self.response = self.c.get('/api/v1/poll.json/')
        self.assertEqual(self.response.status_code, 200)
        self.assertValidJSONResponse(self.response)
        self.assertValidJSON(self.response.content)

    def test_list_view_text(self):
        """Gets the list view in text format"""
        self.response = self.c.get('/api/v1/poll.text/')
        self.assertEqual(self.response.status_code, 200)




# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
