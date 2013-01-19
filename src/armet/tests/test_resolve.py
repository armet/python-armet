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
