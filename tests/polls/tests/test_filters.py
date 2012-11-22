from django.test.client import Client
from . import base
# import json
# from flapjack import encoders


class FiltersTest(base.BaseTest):
    """Unit Tests for the Are You A Tiger poll object"""

    fixtures = ['initial_data']

    def setUp(self):
        """Set up the django HTTP client"""
        self.c = Client()

    def test_id_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])

    def test_id_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])

    def test_choice_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_poll_exact_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    def test_poll_exact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll__not=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

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
        response = self.c.get('/api/v1/choice.json?choice_text__iexact=Yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_iexact_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__iexact__not=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_choice_contains_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__contains=ye')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_contains_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__contains__not=s')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_choice_icontains_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__icontains=yE')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_icontains_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__icontains__not=S')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_id_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gt=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] > 1)

    def test_id_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gt__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] <= 1)

#TODO: Adam do this please!
    # def test_choice_gt_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text=y')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('yes', content[0]['choice_text'])

    # def test_choice_gt_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('yes', content[0]['choice_text'])

    # def test_poll_gt_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__gt=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    # def test_poll_gt_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__not=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gt=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] > 1)

    def test_votes_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gt__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] <= 1)

    def test_id_gte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gte=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] >= 2)

    def test_id_gte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__gte__not=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] < 2)

#TODO: Adam do this please!
    # def test_choice_gte_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text=y')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('yes', content[0]['choice_text'])

    # def test_choice_gte_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('yes', content[0]['choice_text'])

    # def test_poll_gte_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__gte=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    # def test_poll_gte_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__not=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_gte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gte=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] >= 1)

    def test_votes_gte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__gte__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] < 1)

    def test_id_lt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lt=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] < 2)

    def test_id_lt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lt__not=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] >= 2)

#TODO: Adam do this please!
    # def test_choice_lt_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text=y')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('yes', content[0]['choice_text'])

    # def test_choice_lt_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('yes', content[0]['choice_text'])

    # def test_poll_lt_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__gt=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    # def test_poll_lt_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__not=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_lt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lt=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] < 1)

    def test_votes_lt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lt__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] >= 1)

    def test_id_lte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lte=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] <= 2)

    def test_id_lte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__lte__not=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['id'] > 2)

#TODO: Adam do this please!
    # def test_choice_lte_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text=y')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('yes', content[0]['choice_text'])

    # def test_choice_lte_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('yes', content[0]['choice_text'])

    # def test_poll_lte_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__gte=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    # def test_poll_lte_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__not=2')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_lte_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lte=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] <= 1)

    def test_votes_lte_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__lte__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertTrue(content[0]['votes'] > 1)

    def test_id_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__startswith=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(1, content[0]['id'])

    def test_id_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?id__startswith__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])

    def test_choice_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__startswith=y')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__startswith__not=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

#TODO: Adam Voliva 
    # def test_poll_startswith_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__startswith=/a')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    # def test_poll_startswith_not_filter(self):
    #     """Gets the list view in json format"""
    #     response = self.c.get('/api/v1/choice.json?poll__startswith__not=/a')
    #     self.assertHttpOK(response)
    #     self.assertValidJSON(response)
    #     content = self.deserialize(response, type='json')
    #     self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_startswith_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__startswith=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_startswith_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__startswith__not=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(0, content[0]['votes'])
