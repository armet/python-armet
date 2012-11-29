from django.test.client import Client
from flapjack import encoders
from . import base
import json


class ChoiceTest(base.BaseTest):

    # def setUp(self):
    #     pass

    def test_list_view_json(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json/')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_list_view_text(self):
        """Gets the list view in text format"""
        response = self.c.get('/api/v1/choice.text/')
        self.assertHttpOK(response)

    def test_get_choice_json(self):
        """Gets a json listing on a choice"""
        response = self.c.get('/api/v1/choice/1.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_list_json(self):
        """Gets choice file in JSON"""
        response = self.c.get('/api/v1/choice.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_votes_json(self):
        """Gets choice file in JSON"""
        response = self.c.get('/api/v1/choice/1/votes.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_uri_json(self):
        """Gets choice file in JSON"""
        response = self.c.get('/api/v1/choice/1/resource_uri.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_id_json(self):
        """Gets choice file in JSON"""
        response = self.c.get('/api/v1/choice/1/id.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_choicetext_json(self):
        """Gets choice file in JSON"""
        response = self.c.get('/api/v1/choice/1/choice_text.json')
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_post_xml_return_json(self):
        """Test POST on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/1",
            "votes": 5
        }
        response = self.c.post('/api/v1/choice.json/',
            data=encoders.Xml.encode(data).content,
            content_type="application/xml"
        )
        self.assertHttpCreated(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])
        response = self.c.get('/api/v1/choice/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])

    def test_put_xml_return_json(self):
        """Test PUT on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/1",
            "votes": 3
        }
        response = self.c.put('/api/v1/choice/1.json',
            data=encoders.Xml.encode(data).content,
            content_type="application/xml"
        )
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])
        response = self.c.get('/api/v1/choice/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])

    def test_post_json_return_json(self):
        """Test POST on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/1",
            "votes": 5
        }
        response = self.c.post('/api/v1/choice.json/',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpCreated(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])
        response = self.c.get('/api/v1/choice/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])

    def test_put_json_return_json(self):
        """Test PUT on a choice"""
        data = {
            "choice_text": "yes",
            "poll": "/api/v1/poll/1",
            "votes": 3
        }
        response = self.c.put('/api/v1/choice/1.json',
            data=json.dumps(data),
            content_type="application/json"
        )
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])
        response = self.c.get('/api/v1/choice/{}.json/'.format(content['id']))
        self.assertHttpOK(response)
        content = self.deserialize(response)
        self.assertEqual(data['choice_text'], content['choice_text'])

    def test_delete_json(self):
        """Tests delete on choices."""
        response = self.c.delete('/api/v1/choice/2.json')
        self.assertHttpAccepted(response)


# Stuff we should implement in the flapjack REST tester:

# assertResponseisJSON

# assertResponseisText

# assertResponseisXML

# assertHttpOK

# assertHttpCreated
