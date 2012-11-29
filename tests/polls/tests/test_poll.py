# from django.test.client import Client
# from . import base
# import json
from flapjack import test, http


class PollTest(test.TestCase):

    # def setUp(self):
    #     pass

    def test_list_view_json(self):
        """Gets the list view in json format."""
        response = self.client.get('/api/v1/poll.json/')
        self.assertResponse(response, format='json', status=http.client.OK)

    # def test_list_view_text(self):
    #     """Gets the list view in text format."""
    #     response = self.client.get('/api/v1/poll.text/')
    #     self.assertHttpStatus(response, http.client.OK)

    # def test_get_json(self):
    #     """Gets a json listing on a poll."""
    #     response = self.client.get('/api/v1/poll/1.json')
    #     self.assertResponse(response, format='json', status=http.client.OK)

    # def test_get_question_json(self):
    #     """Gets the 'question' attribute from a specific Poll object."""
    #     response = self.client.get('/api/v1/poll/1/question.json')
    #     self.assertResponse(response, format='json', status=http.client.OK)

    # def test_get_resource_uri_json(self):
    #     """Gets the 'resource_uri' attribute from a specific Poll object."""
    #     response = self.client.get('/api/v1/poll/1/resource_uri.json')
    #     self.assertResponse(response, format='json', status=http.client.OK)

    # def test_get_id_json(self):
    #     """Gets the 'id' attribute from a specific Poll object."""
    #     response = self.client.get('/api/v1/poll/1/id.json')
    #     self.assertResponse(response, format='json', status=http.client.OK)

    # def test_get_pub_date_json(self):
    #     """Gets the 'pub_date' attribute from a specific Poll object."""
    #     response = self.client.get('/api/v1/poll/1/pub_date.json')
    #     self.assertResponse(response, format='json', status=http.client.OK)

    # def test_post_xml_return_json(self):
    #     """Test POST on a poll"""
    #     data = {
    #         "pub_date": "2012-11-17T20:39:10+00:00",
    #         "question": "Are you a jiger?"
    #     }
    #     response = self.client.post('/api/v1/poll.json/',
    #         data=encoders.Xml.encode(data).content,
    #         content_type="application/xml"
    #     )
    #     self.assertHttpCreated(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])
    #     response = self.client.get('/api/v1/poll/{}.json/'.format(content['id']))
    #     self.assertHttpOK(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])

    # def test_put_xml_return_json(self):
    #     """Test PUT on a poll"""
    #     data = {
    #         "pub_date": "2012-11-17T20:39:10+00:00",
    #         "question": "Are you a liger?"
    #     }
    #     response = self.client.put('/api/v1/poll/1.json',
    #         data=encoders.Xml.encode(data).content,
    #         content_type="application/xml"
    #     )
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])
    #     response = self.client.get('/api/v1/poll/{}.json/'.format(content['id']))
    #     self.assertHttpOK(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])

    # def test_post_json_return_json(self):
    #     """Test POST on a poll"""
    #     data = {
    #         "pub_date": "2012-11-17T20:39:10+00:00",
    #         "question": "Are you a jiger?"
    #     }
    #     response = self.client.post('/api/v1/poll.json/',
    #         data=json.dumps(data),
    #         content_type="application/json"
    #     )
    #     self.assertHttpCreated(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])
    #     response = self.client.get('/api/v1/poll/{}.json/'.format(content['id']))
    #     self.assertHttpOK(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])

    # def test_put_json_return_json(self):
    #     """Test PUT on a poll"""
    #     data = {
    #         "pub_date": "2012-11-17T20:39:10+00:00",
    #         "question": "Are you a liger?"
    #     }
    #     response = self.client.put('/api/v1/poll/1.json',
    #         data=json.dumps(data),
    #         content_type="application/json"
    #     )
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])
    #     response = self.client.get('/api/v1/poll/{}.json/'.format(content['id']))
    #     self.assertHttpOK(response)
    #     content = self.deserialize(response)
    #     self.assertEqual(data['question'], content['question'])

    # def test_delete_json(self):
    #     """Tests delete on polls."""
    #     response = self.client.delete('/api/v1/poll/2.json')
    #     self.assertHttpAccepted(response)
    #     #Check to make sure the choices are deleted too
    #     response = self.client.get('/api/v1/choice/5.json')
    #     self.assertHttpNotFound(response)
    #     response = self.client.get('/api/v1/choice/6.json')
    #     self.assertHttpNotFound(response)
    #     response = self.client.get('/api/v1/choice/7.json')
    #     self.assertHttpNotFound(response)
    #     response = self.client.get('/api/v1/choice/8.json')
    #     self.assertHttpNotFound(response)
