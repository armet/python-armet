from django.test.client import RequestFactory
# from . import base
# import json
from flapjack import test
from polls import api


class ReverseTest(test.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_choice_reverse_list(self):
        path = '/api/v1/choice'
        request = self.factory.get(path)
        url = api.Choice(request).reverse()
        self.assertEqual(path, url)

    # def test_choice_reverse_individual(self):
    #     url = api.Choice.reverse(15)
    #     self.assertEqual('/api/v1/choice/15', url)

    # def test_poll_reverse_list(self):
    #     url = api.Poll.reverse()
    #     self.assertEqual('/api/v1/poll', url)

    # def test_poll_reverse_individual(self):
    #     url = api.Poll.reverse(api.Poll.model(id=85))
    #     self.assertEqual('/api/v1/poll/85', url)
