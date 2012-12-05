# from flapjack import testing
# from flapjack.http import status
# #from django.utils import unittest
# #from django.test.client import Client
# from lxml import etree
# import json

# #class TigerTest(unittest.TestCase):
# class TigerTest(testing.FlapjackUnitTest):
#     """Unit Tests for the Are You A Tiger poll object"""

# #    def setUp(self):
# #        """Set up the django HTTP client"""
# #        self.c = Client()

#     def test_list_view_xml(self):
#         """Gets the list view in xml format"""
#         response = self.c.get('/api/v1/poll.xml/')
#         self.assertOKValidXML(response)

#     def test_list_view_xml_2(self):
#         """Gets the list view in xml format"""
#         response = self.c.get('/api/v1/poll', HTTP_ACCEPT='application/xml')
#         self.assertOKValidXML(response)


#     def test_list_view_json(self):
#         """Gets the list view in json format"""
#         response = self.c.get('/api/v1/poll.json/')
#         self.assertOKValidJSON(response)

#     def test_list_view_json_2(self):
#         """Gets the list view in json format"""
#         response = self.c.get('/api/v1/poll', HTTP_ACCEPT='application/json')
#         self.assertOKValidJSON(response)

#     def test_list_view_text(self):
#         """Gets the list view in text format"""
#         response = self.c.get('/api/v1/poll.text/')
#         self.assertOKResponse(response)

#     def test_list_view_text_2(self):
#         """Gets the list view in text format"""
#         response = self.c.get('/api/v1/poll', HTTP_ACCEPT='text/plain')
#         self.assertOKResponse(response)

#     def test_get_poll_file_json(self):
#         """Gets poll file in JSON"""
#         response = self.c.get('/api/v1/poll/1/file.json')
#         self.assertOKValidJSON(response)

#     def test_get_choice_list_json(self):
#         """Gets poll file in JSON"""
#         response = self.c.get('/api/v1/choice.json')
#         self.assertOKValidJSON(response)

#     def test_get_choice_json(self):
#         """Gets poll file in JSON"""
#         response = self.c.get('/api/v1/choice/1.json')
#         self.assertOKValidJSON(response)

# #    def test_fooo(self):
# #        """Gets poll file in JSON"""
# #        response = self.c.get('/api/v1/choice/1.json')
# #        print 'fooo'
# #        print response['Content-Type']

# # Stuff we should implement in the flapjack REST tester:

# # assertResponseisJSON

# # assertResponseisText

# # assertResponseisXML

# # assertHttpOK

# # assertHttpCreated
