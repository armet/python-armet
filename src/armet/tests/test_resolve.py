from django.test.client import RequestFactory
from armet.utils import test
from armet.resources import Resource
from armet.tests.models import Choice, Poll


class Resolve(Resource):
    pass


class ResolveTestCase(test.TestCase):

    def setUp(self):
        super(ResolveTestCase, self).setUp()
        self.poll_endpoint = '/poll'
        self.choice_endpoint = '/choice'

    def test_resolve_poll(self):
        """Test the resolvability of a poll url."""

        # Test all the polls.
        request = RequestFactory().get(self.poll_endpoint)
        objs = Resolve(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.all(), objs)

        # Test a specific poll.
        poll_number = 1
        request = RequestFactory().get('{}/{}'.format(self.poll_endpoint,
                                                      poll_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Poll.objects.get(pk=poll_number), obj)

        # Try that again as a query string with id.
        poll_number = 1
        request = RequestFactory().get('{}?id={}'.format(self.poll_endpoint,
                                                         poll_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Poll.objects.get(pk=poll_number), obj)

        # Try that again as a query string with pk.
        poll_number = 1
        request = RequestFactory().get('{}?pk={}'.format(self.poll_endpoint,
                                                         poll_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Poll.objects.get(pk=poll_number), obj)

        # Should check the question here, but it's not working.

        # Try a pub_date.
        poll_date = '2012-12-11T16:20:46.016Z'
        query_string = '{}?pub_date={}'.format(self.poll_endpoint, poll_date)
        request = RequestFactory().get(query_string)
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Poll.objects.get(pub_date=poll_date), obj)

    def test_resolve_choice(self):
        """Test the resolvability of a choice url."""
        # Test all the choices.
        request = RequestFactory().get(self.choice_endpoint)
        objs = Resolve(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.all(), objs)
        # Test a specific choice.
        choice_number = 1
        request = RequestFactory().get('{}/{}'.format(self.choice_endpoint,
                                                      choice_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Choice.objects.get(pk=choice_number), obj)

        # Try that again as a query string with id.
        choice_number = 1
        request = RequestFactory().get('{}?id={}'.format(self.choice_endpoint,
                                                         choice_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Choice.objects.get(pk=choice_number), obj)

        # Try that again as a query string with pk.
        choice_number = 1
        request = RequestFactory().get('{}?pk={}'.format(self.choice_endpoint,
                                                         choice_number))
        # Returns a list, so grab the first one.
        obj = Resolve(request=request).resolve(request.path)[0]
        self.assertEquals(Choice.objects.get(pk=choice_number), obj)
