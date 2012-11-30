# from django.test.client import Client
# from . import base
# import urllib
# # import json
# # from flapjack import encoders


# class FiltersTest(base.BaseTest):
#     """Unit Tests for the Are You A Tiger poll object"""

#     fixtures = ['initial_data']

#     def setUp(self):
#         """Set up the django HTTP client"""
#         self.c = Client()
#         self.endpoint = '/api/v1/choice.json?'

#     def test_id_exact_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(1, content[0]['id'])

#     def test_id_exact_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(1, content[0]['id'])

#     def test_choice_exact_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text', 'yes')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_exact_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__not', 'yes')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

#     def test_poll_exact_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('poll', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     def test_poll_exact_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('poll__not', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

#     def test_votes_exact_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(0, content[0]['votes'])

#     def test_votes_exact_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__not', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(0, content[0]['votes'])

#     def test_choice_iexact_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iexact', 'YeS')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_iexact_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iexact__not', 'YeS')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

#     def test_choice_contains_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__contains', 'es')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_contains_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__contains__not', 'es')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

#     def test_choice_icontains_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__icontains', 'Es')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_icontains_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__icontains__not', 'eS')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

#     def test_id_gt_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__gt', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] > 1)

#     def test_id_gt_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__gt__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] <= 1)

# #TODO: Adam do this please!
#     # def test_choice_gt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_gt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_gt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__gt=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_gt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_gt_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__gt', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] > 1)

#     def test_votes_gt_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__gt__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] <= 1)

#     def test_id_gte_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__gte', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] >= 2)

#     def test_id_gte_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__gte__not', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] < 2)

# #TODO: Adam do this please!
#     # def test_choice_gte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_gte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_gte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__gte=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_gte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_gte_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__gte', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] >= 1)

#     def test_votes_gte_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__gte__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] < 1)

#     def test_id_lt_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__lt', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] < 2)

#     def test_id_lt_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__lt__not', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] >= 2)

# #TODO: Adam do this please!
#     # def test_choice_lt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_lt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_lt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__gt=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_lt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_lt_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__lt', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] < 1)

#     def test_votes_lt_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__lt__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] >= 1)

#     def test_id_lte_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__lte', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] <= 2)

#     def test_id_lte_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__lt__not', 2)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['id'] > 2)

# #TODO: Adam do this please!
#     # def test_choice_lte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_lte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_lte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__gte=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_lte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_lte_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__lte', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] <= 1)

#     def test_votes_lte_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__lte__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertTrue(content[0]['votes'] > 1)

#     def test_id_startswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__startswith', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(1, content[0]['id'])

#     def test_id_startswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__startswith__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(1, content[0]['id'])

#     def test_choice_startswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__startswith', 'y')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_startswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__startswith__not', 'ye')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_startswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__startswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_startswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__startswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_startswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__startswith', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(0, content[0]['votes'])

#     def test_votes_startswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__startswith__not', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(0, content[0]['votes'])

#     def test_id_istartswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__istartswith', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(1, content[0]['id'])

#     def test_id_istartswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__istartswith__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(1, content[0]['id'])

#     def test_choice_istartswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__istartswith', 'y')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_istartswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__istartswith__not', 'Ye')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_startswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__startswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_startswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__startswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_istartswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__istartswith', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(0, content[0]['votes'])

#     def test_votes_istartswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__istartswith__not', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(0, content[0]['votes'])

#     def test_id_endswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__endswith', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(1, content[0]['id'])

#     def test_id_endswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__endswith__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(1, content[0]['id'])

#     def test_choice_endswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__endswith', 's')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_endswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__endswith__not', 's')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_endswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__endswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_endswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__endswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_endswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__endswith', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(0, content[0]['votes'])

#     def test_votes_endswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__endswith__not', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(0, content[0]['votes'])

#     def test_id_iendswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__iendswith', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(1, content[0]['id'])

#     def test_id_iendswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('id__iendswith__not', 1)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(1, content[0]['id'])

#     def test_choice_iendswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iendswith', 'S')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_iendswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iendswith__not', 'Es')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_iendswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__iendswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_iendswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__iendswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     def test_votes_iendswith_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__iendswith', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual(0, content[0]['votes'])

#     def test_votes_iendswith_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('votes__iendswith__not', 0)])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual(0, content[0]['votes'])


# #TODO: __isnull filter


#     # def test_id_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?id__regex=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual(1, content[0]['id'])

#     # def test_id_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?id__regex__not=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual(1, content[0]['id'])

#     def test_choice_regex_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__regex', '[y][e][s]')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_regex_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__regex__not', '[y][e][s]')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__regex=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_poll_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?poll__regex__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('self.endpoint + poll/2', content[0]['poll'])

#     # def test_votes_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?votes__regex=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual(0, content[0]['votes'])

#     # def test_votes_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('self.endpoint + choice.json?votes__regex__not=0')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual(0, content[0]['votes'])


#     ##iregex

#     def test_choice_iregex_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iregex', '[y][E][s]')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_iregex_not_filter(self):
#         """Gets the list view in json format"""
#         query_string = urllib.urlencode([('choice_text__iregex__not', '[Y][E][s]')])
#         response = self.c.get(self.endpoint + query_string)
#         content = self.assertValidJSONResponse(response)
#         self.assertNotEqual('yes', content[0]['choice_text'])
