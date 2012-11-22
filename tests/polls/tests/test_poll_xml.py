from django.test.client import Client
from . import base
import json
from flapjack import encoders
from datetime import datetime


class TigerTestXML(base.BaseTest):
    """Unit Tests for the Are You A Tiger poll object"""

    fixtures = ['initial_data']

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_list_view_xml(self):
        """Gets the list view in xml format"""
        response = self.c.get('/api/v1/poll.xml/')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/poll.text/')
        self.assertHttpOK(response)

    def test_get_poll_xml(self):
        """Gets a xml listing on a poll"""
        response = self.c.get('/api/v1/poll/1.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_file_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/file.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_list_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/choice.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_choice_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/choice/1.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_question_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/question.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_uri_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/resource_uri.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_id_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/id.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_get_poll_pubdate_xml(self):
        """Gets poll file in xml"""
        response = self.c.get('/api/v1/poll/1/pub_date.xml')
        self.assertHttpOK(response)
        self.assertValidXML(response)

    def test_post_xml_return_xml(self):
        """Test POST on a poll"""
        data = {
            "pub_date": datetime.now(),
            "question": "Are you a liger?"
        }
        response = self.c.post('/api/v1/poll.xml/',
            data=encoders.Xml.encode(data).content,
            content_type="application/xml"
        )
        self.assertHttpCreated(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response, type='xml')
        self.assertEqual(data['question'], content['question'])

    def test_put_xml_return_xml(self):
        """Test PUT on a poll"""
        data = {
            "pub_date": datetime.now(),
            "question": "Are you a liger?"
        }
        response = self.c.post('/api/v1/poll.xml/',
            data=encoders.Xml.encode(data).content,
            content_type="application/xml"
        )
        self.assertHttpOK(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response, type='xml')
        self.assertEqual(data['question'], content['question'])

    def test_post_json_return_xml(self):
        """Test POST on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a jiger?"
        }
        response = self.c.post('/api/v1/poll.xml/',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpCreated(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response, type='xml')
        self.assertEqual(data['question'], content['question'])

    def test_put_json_return_xml(self):
        """Test PUT on a poll"""
        data = {
            "pub_date": "2012-11-17T20:39:10+00:00",
            "question": "Are you a liger?"
        }
        response = self.c.put('/api/v1/poll/1.xml',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpOK(response)
        self.assertValidXML(response)
        content = self.deserialize(response, type='xml')

        self.assertEqual(data['question'], content['question'])
        response = self.c.get('/api/v1/poll/{}.xml/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response, type='xml')
        self.assertEqual(data['question'], content['question'])

    def test_delete_xml(self):
        """Tests delete on polls."""
        response = self.c.delete('/api/v1/poll/2.xml')
        self.assertEqual(response.status_code, 204)
        #Check to make sure the choices are deleted too
        response = self.c.get('/api/v1/choice/5.xml')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/6.xml')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/7.xml')
        self.assertHttpNotFound(response)
        response = self.c.get('/api/v1/choice/8.xml')
        self.assertHttpNotFound(response)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
