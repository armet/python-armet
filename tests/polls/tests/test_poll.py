from django.utils import unittest
from django.test.client import Client
from lxml import etree
from . import base
import json
# from django.core.management import call_command


class TigerTest(base.BaseTest):
    """Unit Tests for the Are You A Tiger poll object"""

    fixtures = ['initial_data']

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()
        # call_command('loaddata', 'tests/ponies', verbosity=0)

    def test_list_view_json(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/poll.json/')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/poll.text/')
        self.assertHttpOK(response)

    def test_get_poll_json(self):
        """Gets a json listing on a poll"""
        response = self.c.get('/api/v1/poll/1.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_poll_file_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/file.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_list_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/choice.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/choice/1.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_poll_question_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/question.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_poll_uri_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/resource_uri.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_poll_id_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/id.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_poll_pubdate_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/pub_date.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_post_json(self):
        """Test POST on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a jiger?"
        }
        response = self.c.post('/api/v1/poll.json/',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpCreated(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['question'], content['question'])

    def test_put_json(self):
        """Test PUT on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a liger?"
        }
        response = self.c.put('/api/v1/poll/1.json',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['question'], content['question'])

    def test_delete_json(self):
        """Tests delete on polls."""
        response = self.c.delete('/api/v1/poll/2.json')
        self.assertHttpAccepted(response)
        #Check to make sure the choices are deleted too
        response = self.c.get('/api/v1/choice/5.json')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/6.json')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/7.json')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/8.json')
        self.assertHttpNotFound(response)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
