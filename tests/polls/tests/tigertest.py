from django.utils import unittest
from django.test.client import Client
from lxml import etree
import json


class TigerTest(unittest.TestCase):
    """Unit Tests for the Are You A Tiger poll object"""

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_list_view_xml(self):
        """Gets the list view in xml format"""
        response = self.c.get('/api/v1/poll.xml/')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_list_view_json(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/poll.json/')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/poll.text/')
        self.assertEqual(response.status_code, 200)

    def test_get_poll_json(self):
        """Gets a json listing on a poll"""
        response = self.c.get('/api/v1/poll/1.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_poll_file_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/file.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_choice_list_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/choice.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_choice_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/choice/1.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_poll_question_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/question.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_poll_uri_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/resource_uri.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_poll_id_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/id.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

    def test_get_poll_pubdate_json(self):
        """Gets poll file in JSON"""
        response = self.c.get('/api/v1/poll/1/pub_date.json')
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')

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
        self.assertEqual(response.status_code, 201)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')
        content = json.loads(response.content)
        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.json/'.format(content['id']))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
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
        self.assertEqual(response.status_code, 200)
        try:
            json.loads(response.content)
        except ValueError:
            self.assertEqual(False, 'This is not really JSON!')
        content = json.loads(response.content)
        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.json/'.format(content['id']))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(data['question'], content['question'])

    def test_delete_json(self):
        """Tests delete on polls."""
        response = self.c.delete('/api/v1/poll/2.json')
        self.assertEqual(response.status_code, 204)
        response = self.c.get('/api/v1/choice/5.json')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/6.json')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/7.json')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/8.json')
        self.assertEqual(response.status_code, 404)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
