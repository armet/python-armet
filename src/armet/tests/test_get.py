from .hub import HubTest
from .base import BaseTest


class ChoiceTest(HubTest, BaseTest):

    endpoint = '/'
    model = 'choice'

    def setUp(self):
        super(ChoiceTest, self).setUp()


class PollTest(HubTest, BaseTest):

    endpoint = '/'
    model = 'poll'

    def setUp(self):
        super(PollTest, self).setUp()
