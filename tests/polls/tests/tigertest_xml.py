from django.utils import unittest
from django.test.client import Client
from lxml import etree
import json


class TigerTestXML(unittest.TestCase):
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

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/poll.text/')
        self.assertEqual(response.status_code, 200)

    def test_get_poll_xml(self):
        """Gets a xml listing on a poll"""
        response = self.c.get('/api/v1/poll/1.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_poll_file_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/file.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_choice_list_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/choice.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_choice_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/choice/1.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_poll_question_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/question.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_poll_uri_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/resource_uri.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_poll_id_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/id.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_get_poll_pubdate_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/pub_date.xml')
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')

    def test_post_xml(self):
        """Test POST on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a jiger?"
        }
        response = self.c.post('/api/v1/poll.xml/',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')
        #print(response.content)
        content = etree.fromstring(response.content)
        content = dict((x.get('name'), x.text)
            for x in content.findall('attribute'))

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertEqual(response.status_code, 200)
        content = etree.fromstring(response.content)
        content = dict((x.get('name'), x.text)
            for x in content.findall('attribute'))
        self.assertEqual(data['question'], content['question'])

    def test_put_xml(self):
        """Test PUT on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a liger?"
        }
        response = self.c.put('/api/v1/poll/1.xml',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            self.assertEqual(False, 'This is not XML!')
        #print(response.content)
        content = etree.fromstring(response.content)
        content = dict((x.get('name'), x.text)
            for x in content.findall('attribute'))

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertEqual(response.status_code, 200)
        content = etree.fromstring(response.content)
        content = dict((x.get('name'), x.text)
            for x in content.findall('attribute'))
        self.assertEqual(data['question'], content['question'])

    def test_delete_xml(self):
        """Tests delete on polls."""
        response = self.c.delete('/api/v1/poll/2.xml')
        self.assertEqual(response.status_code, 204)
        #Check to make sure the choices are deleted too
        response = self.c.get('/api/v1/choice/5.xml')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/6.xml')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/7.xml')
        self.assertEqual(response.status_code, 404)
        response = self.c.get('/api/v1/choice/8.xml')
        self.assertEqual(response.status_code, 404)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
