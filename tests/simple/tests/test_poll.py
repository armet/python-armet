import json
from django.test import TestCase
from flapjack.http import constants
from .base import Base
from .alive import Alive


class Poll(Base, Alive, TestCase):

    name = 'poll'

    def test_count(self):
        response = self.get(self.path, "application/json")
        self.assertEqual(response.status_code, constants.OK)

        data = json.loads(response.content)
        self.assertEqual(len(data), 7)
