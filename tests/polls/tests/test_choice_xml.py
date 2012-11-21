from django.utils import unittest
from django.test.client import Client
from lxml import etree
import json
from . import base


class ChoiceTestXML(base.BaseTest):
    """Unit Tests for the Are You A Tiger choice object"""

    fixtures = ['initial_data']

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_list_view_xml(self):
        """Gets the list view in xml format"""
        response = self.c.get('/api/v1/choice.xml/')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/choice.text/')
        self.assertHttpOK(response)

    def test_get_choice_xml(self):
        """Gets a xml listing on a choice"""
        response = self.c.get('/api/v1/choice/1.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_list_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice/1.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)
    def test_get_choice_votes_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice/1/votes.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_uri_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice/1/resource_uri.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_id_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice/1/id.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_choicetext_xml(self):
        """Gets choice file in xml"""
        response = self.c.get('/api/v1/choice/1/choice_text.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_post_xml(self):
        """Test POST on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/2",
            "votes": 0
        }
        response = self.c.post('/api/v1/choice.xml/',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpCreated(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)

    def test_put_xml(self):
        """Test PUT on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/1",
            "votes": 3
        }
        response = self.c.put('/api/v1/choice/1.xml',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpOK(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)

    def test_delete_xml(self):
        """Tests delete on choices."""
        response = self.c.delete('/api/v1/choice/6.xml')
        self.assertHttpAccepted(response)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisxml

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
