from django.test.client import Client
from . import base
# import json
# from flapjack import encoders


class FiltersOrTest(base.BaseTest):
    """Unit Tests for the Are You A Tiger poll object"""

    fixtures = ['initial_data']

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_id_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])
        #self.assertEqual(2, content[1]['id'])

    def test_id_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])
        #self.assertNotEqual(2, content[1]['id'])

    def test_choice_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text=yes,no')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])
        #self.assertEqual('no', content[1]['choice_text'])

    def test_choice_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__not=yes,no')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])
        #self.assertNotEqual('no', content[1]['choice_text'])

    def test_poll_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll=2,3')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('/api/v1/poll/2', content[0]['poll'])
        #self.assertEqual('/api/v1/poll/3', content[1]['poll'])

    def test_poll_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll__not=2,3')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])
        #self.assertNotEqual('/api/v1/poll/3', content[1]['poll'])

    def test_votes_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__not=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])

    def test_choice_iexact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iexact=Yes,yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_iexact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iexact__not=yes,Yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_choice_contains_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__contains=ye,s')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_contains_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__contains__not=ye,s')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_choice_icontains_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__icontains=yE,S,s')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_icontains_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__icontains__not=yE,S,s')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_id_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gt=1,0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] > 1)

    def test_id_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gt__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] <= 1)

# #TODO: Adam do this please!
#     # def test_choice_gt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_gt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_gt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__gt=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_gt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gt=1,0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] > 1)

    def test_votes_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gt__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] <= 1)

    def test_id_gte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gte=2,1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] >= 2)

    def test_id_gte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gte__not=2,3')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] < 2)

# #TODO: Adam do this please!
#     # def test_choice_gte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_gte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_gte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__gte=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_gte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_gte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gte=1,0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] >= 1)
        self.assertFalse(content[0]['votes'] < 1)

    def test_votes_gte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gte__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] < 1)
        self.assertFalse(content[0]['votes'] >= 1)
        self.assertTrue(content[0]['votes'] < 2)
        self.assertFalse(content[0]['votes'] >= 2)

    def test_id_lt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lt=2,1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] < 2)
        self.assertFalse(content[0]['id'] >= 2)

    def test_id_lt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lt__not=2,3')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] >= 2)
        self.assertFalse(content[0]['id'] < 2)
        self.assertTrue(content[0]['id'] >= 3)
        self.assertFalse(content[0]['id'] < 3)

# #TODO: Adam do this please!
#     # def test_choice_lt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_lt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_lt_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__gt=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_lt_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_lt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lt=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] < 1)
        self.assertFalse(content[0]['votes'] >= 1)
        self.assertTrue(content[0]['votes'] < 2)
        self.assertFalse(content[0]['votes'] >= 2)

    def test_votes_lt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lt__not=1,0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] >= 1)
        self.assertFalse(content[0]['votes'] < 1)

    def test_id_lte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lte=2,1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] <= 2)
        self.assertFalse(content[0]['id'] > 2)
        self.assertTrue(content[0]['id'] <= 1)
        self.assertFalse(content[0]['id'] > 1)

    def test_id_lte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lte__not=2,3')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] > 2)
        self.assertFalse(content[0]['id'] <= 2)
        self.assertTrue(content[0]['id'] > 3)
        self.assertFalse(content[0]['id'] <= 3)

# #TODO: Adam do this please!
#     # def test_choice_lte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text=y')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('yes', content[0]['choice_text'])

#     # def test_choice_lte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('yes', content[0]['choice_text'])

#     # def test_poll_lte_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__gte=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_lte_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__not=2')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_lte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lte=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] <= 1)
        self.assertFalse(content[0]['votes'] > 1)
        self.assertTrue(content[0]['votes'] <= 2)
        self.assertFalse(content[0]['votes'] > 2)

    def test_votes_lte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lte__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] > 1)
        self.assertFalse(content[0]['votes'] <= 1)
        self.assertTrue(content[0]['votes'] > 2)
        self.assertFalse(content[0]['votes'] <= 2)

    def test_id_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__startswith=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])
        self.assertEqual(10, content[1]['id'])
        self.assertEqual(11, content[2]['id'])
        self.assertEqual(12, content[3]['id'])

    def test_id_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__startswith__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])
        self.assertNotEqual(2, content[0]['id'])

    def test_choice_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__startswith=y,yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__startswith__not=y,yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_startswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__startswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_startswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__startswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__startswith=0,5')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__startswith__not=0,5')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])
        self.assertNotEqual(5, content[0]['votes'])

    def test_id_istartswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__istartswith=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])

    def test_id_istartswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__istartswith__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])
        self.assertNotEqual(2, content[0]['id'])

    def test_choice_istartswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__istartswith=y,Y')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_istartswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__istartswith__not=yes,YeS,YES,Y')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_startswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__startswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_startswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__startswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_istartswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__istartswith=0,5')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_istartswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__istartswith__not=0,5')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])

    def test_id_endswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__endswith=1,111')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])

    def test_id_endswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__endswith__not=1,111')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])

    def test_choice_endswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__endswith=s,es')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_endswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__endswith__not=yes,es')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_endswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__endswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_endswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__endswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_endswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__endswith=0,1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_endswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__endswith__not=0,1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])

    def test_id_iendswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__iendswith=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])

    def test_id_iendswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__iendswith__not=1,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])

    def test_choice_iendswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iendswith=S,Es')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_iendswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iendswith__not=yeS,eS')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

# #TODO: Adam Voliva
#     # def test_poll_iendswith_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__iendswith=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_iendswith_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__iendswith__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_iendswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__iendswith=0,5')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_iendswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__iendswith__not=0,2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])
        self.assertNotEqual(2, content[0]['votes'])

# #TODO: __isnull filter

#     # def test_id_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?id__regex=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual(1, content[0]['id'])

#     # def test_id_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?id__regex__not=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual(1, content[0]['id'])

#     def test_choice_regex_filter(self):
#         """Gets the list view in json format"""
#         response = self.c.get('/api/v1/choice.json?\
#             choice_text__regex=[y][e][s]')
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         content = self.deserialize(response, type='json')
#         self.assertEqual('yes', content[0]['choice_text'])

#     def test_choice_regex_not_filter(self):
#         """Gets the list view in json format"""
#         response = self.c.get('/api/v1/choice.json?\
#             choice_text__regex__not=[y][e][s]')
#         self.assertHttpOK(response)
#         self.assertValidJSON(response)
#         content = self.deserialize(response, type='json')
#         self.assertNotEqual('yes', content[0]['choice_text'])

#     #TODO: Adam Voliva

#     # def test_poll_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__regex=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_poll_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?poll__regex__not=/a')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

#     # def test_votes_regex_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?votes__regex=[0-9]')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertEqual(0, content[0]['votes'])

#     # def test_votes_regex_not_filter(self):
#     #     """Gets the list view in json format"""
#     #     response = self.c.get('/api/v1/choice.json?votes__regex__not=0')
#     #     self.assertHttpOK(response)
#     #     self.assertValidJSON(response)
#     #     content = self.deserialize(response, type='json')
#     #     self.assertNotEqual(0, content[0]['votes'])

#     ##iregex
    def test_choice_iregex_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iregex=[y][e][s]')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_iregex_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iregex__not=[y][e][s]')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])
