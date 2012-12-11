from .hub import HubTest
from .base import BaseTest
from armet.utils import test
from armet import http


class GetBase(object):
    """Common test cases for GET operations."""

    formats = ('json', 'xml')

    def test_list(self):
        """Asserts the list view returns valid content."""
        for format in self.formats:
            url = '{}{}.{}'.format(self.endpoint, self.model, format)
            response = self.client.get(url)

            self.deserialize(response, format)
            self.assertHttpStatus(response, http.client.OK)


class ChoiceTest(GetBase, BaseTest, test.TestCase):

    endpoint = '/'
    model = 'choice'

    def setUp(self):
        super(ChoiceTest, self).setUp()

    def test_get_choice_votes(self):
        """Gets choice votes"""
        response = self.client.get(self.endpoint + 'choice/1/votes.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/votes.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_uri(self):
        """Gets choice resource_uri"""
        response = self.client.get(self.endpoint + 'choice/1/resource_uri.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/resource_uri.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_id(self):
        """Gets choice id"""
        response = self.client.get(self.endpoint + 'choice/1/id.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/id.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)

    def test_get_choice_choicetext(self):
        """Gets choice text"""
        response = self.client.get(self.endpoint + 'choice/1/choice_text.{}/'
            .format('xml'))
        self.assertHttpOK(response)
        self.assertValidXML(response)
        response = self.client.get(self.endpoint + 'choice/1/choice_text.{}/'
            .format('json'))
        self.assertHttpOK(response)
        self.assertValidJSON(response)


class PollTest(GetBase, BaseTest, test.TestCase):

    endpoint = '/'
    model = 'poll'

    def setUp(self):
        super(PollTest, self).setUp()
