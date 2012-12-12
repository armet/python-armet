# from django.utils import unittest
# from django.test.client import Client
# from .base import BaseTest
# from .models import Choice, Poll


# class HubTest(object):
#     """Unit Tests for Invitation related API calls"""

#     fixtures = ['initial_data']

#     def setUp(self):
#         """Sets up a user and HTTP Django test clients
#         """
#         super(HubTest, self).setUp()
#         self.c = Client()
#         self.poll = Poll.objects.create(
#             question="Why???",
#             pub_date='2012-11-17T20:39:10+00:00'
#         )
#         self.choice_one = Choice.objects.create(
#             poll=self.poll,
#             choice_text="Because...",
#             votes=5
#         )

#     def tearDown(self):
#         """
#         Cleans up the user object
#         """
#         super(HubTest, self).tearDown()

#     def test_list_view(self):
#         """Gets the list view"""
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_get_choice(self):
#         """Gets a listing on a choice"""
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_get_choice_list(self):
#         """Gets choice list"""
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + self.model + '.{}/'.format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)



#     def test_get_choice_votes(self):
#         """Gets choice votes"""
#         response = self.c.get(self.endpoint + 'choice/1/votes.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + 'choice/1/votes.{}/'
#             .format('json'))def test_get_poll_question_xml(self):
#         """Gets poll file in xml"""
#         response = self.c.get(self.endpoint + 'poll/1/question.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         response = self.c.get(self.endpoint + 'poll/1/question.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)

#     def test_get_poll_uri_xml(self):
#         """Gets poll file in xml"""
#         response = self.c.get(self.endpoint + 'poll/1/resource_uri.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         response = self.c.get(self.endpoint + 'poll/1/resource_uri.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)

#     def test_get_poll_id_xml(self):
#         """Gets poll file in xml"""
#         response = self.c.get(self.endpoint + 'poll/1/id.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         response = self.c.get(self.endpoint + 'poll/1/id.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)

#     def test_get_poll_pubdate_xml(self):
#         """Gets poll file in xml"""
#         response = self.c.get(self.endpoint + 'poll/1/pub_date.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         response = self.c.get(self.endpoint + 'poll/1/pub_date.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_get_choice_uri(self):
#         """Gets choice resource_uri"""
#         response = self.c.get(self.endpoint + 'choice/1/resource_uri.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + 'choice/1/resource_uri.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_get_choice_id(self):
#         """Gets choice id"""
#         response = self.c.get(self.endpoint + 'choice/1/id.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + 'choice/1/id.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_get_choice_choicetext(self):
#         """Gets choice text"""
#         response = self.c.get(self.endpoint + 'choice/1/choice_text.{}/'
#             .format('xml'))
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
#         response = self.c.get(self.endpoint + 'choice/1/choice_text.{}/'
#             .format('json'))
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)

#     def test_recursiveness(self):
#         response = self.c.get(self.endpoint +
#             'poll/1/choices/1/poll/choices/1/poll/choices/1/poll/choices/' +
#             '1/poll/choices/1/poll/choices/1/poll/choices/1/poll/choices/' +
#             '1/poll/choices/1/poll/choices/1/poll/choices/1.{}/'
#             .format('xml')
#         )
#         self.assertHttpOK(response)
#         self.assertValidXML(response)
