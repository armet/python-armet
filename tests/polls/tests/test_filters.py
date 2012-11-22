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
        response = self.c.get('/api/v1/choice.json?id__not=1')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual(1, content[0]['id'])

    def test_choice_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('yes', content[0]['choice_text'])

    def test_choice_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?choice_text__not=yes')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('yes', content[0]['choice_text'])

    def test_poll_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual('/api/v1/poll/2', content[0]['poll'])

    def test_poll_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?poll__not=2')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertNotEqual('/api/v1/poll/2', content[0]['poll'])

    def test_votes_gt_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
        self.assertEqual(0, content[0]['votes'])

    def test_votes_gt_not_filter(self):
        """Gets the list view in json format"""
        response = self.c.get('/api/v1/choice.json?votes__not=0')
        self.assertHttpOK(response)
        self.assertValidJSON(response)
        content = self.deserialize(response, type='json')
