# from django.test import TestCase
# from django.test.client import RequestFactory
from flapjack.http import constants


class Alive(object):

    def test_alive(self):
        response = self.get(self.path, "application/json")
        self.assertEqual(response.status_code, constants.OK)
