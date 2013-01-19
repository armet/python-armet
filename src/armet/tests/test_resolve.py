from django.test.client import RequestFactory
from armet.utils import test
from armet.resources import Resource
from armet.tests.models import Choice, Poll


class ResolveTestCase(test.TestCase):

    def setUp(self):
        super(ResolveTestCase, self).setUp()
        self.poll_endpoint = '/poll'
        self.choice_endpoint = '/choice'

    def test_resolve_poll(self):
        """Test the resolvability of a poll url."""

        # Test all the polls.
        request = RequestFactory().get(self.poll_endpoint)
        objs = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.all(), objs)

        # Test a specific poll.
        poll_number = 1
        request = RequestFactory().get('{}/{}'.format(self.poll_endpoint,
                                                      poll_number))
        # Has the possibility of failure.
        obj = Resource(request=request).resolve(request.path)
        try:
            poll_obj = Poll.objects.get(pk=poll_number)
            # Wrap this in a list and test it.
            self.assertItemsEqual([poll_obj], obj)
        except Poll.DoesNotExist:
            self.assertItemsEqual([], obj)
        # Try that again as a query string with id.
        poll_number = 1
        request = RequestFactory().get('{}?id={}'.format(self.poll_endpoint,
                                                         poll_number))
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.filter(pk=poll_number), obj)

        # Try that again as a query string with pk.
        poll_number = 1
        request = RequestFactory().get('{}?pk={}'.format(self.poll_endpoint,
                                                         poll_number))
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.filter(pk=poll_number), obj)

        # Try a question.
        question = "Did you dream last night?"
        query_string = '{}?question={}'.format(self.poll_endpoint, question)
        request = RequestFactory().get(query_string)
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.filter(question=question), obj)

        # Try a pub_date.
        poll_date = '2012-12-11T16:20:46.016Z'
        query_string = '{}?pub_date={}'.format(self.poll_endpoint, poll_date)
        request = RequestFactory().get(query_string)
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.filter(pub_date=poll_date), obj)

    def test_resolve_choice(self):
        """Test the resolvability of a choice url."""

        # Test all the choices.
        request = RequestFactory().get(self.choice_endpoint)
        objs = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.all(), objs)

        # Test a specific choice.
        choice_number = 1
        request = RequestFactory().get('{}/{}'.format(self.choice_endpoint,
                                                      choice_number))
        # Has the possibility of failure.
        obj = Resource(request=request).resolve(request.path)
        try:
            choice_obj = Choice.objects.get(pk=choice_number)
            # Wrap this in a list and test it.
            self.assertItemsEqual([choice_obj], obj)
        except Choice.DoesNotExist:
            self.assertItemsEqual([], obj)

        # Try that again as a query string with id.
        choice_number = 14654135
        request = RequestFactory().get('{}?id={}'.format(self.choice_endpoint,
                                                         choice_number))
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.filter(pk=choice_number), obj)

        # Try that again as a query string with pk.
        choice_number = 1
        request = RequestFactory().get('{}?pk={}'.format(self.choice_endpoint,
                                                         choice_number))
        # Returns a list, so grab the first one.
        obj = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.filter(pk=choice_number), obj)

        # Try with a poll query.
        poll_number = 63
        query = '{}?poll={}'.format(self.choice_endpoint, poll_number)
        request = RequestFactory().get(query)
        # Returns a list, so grab the first one.
        objs = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.filter(poll=poll_number), objs)

        # Try with a choice_text query.
        text = 'Maybe'
        query = '{}?choice_text={}'.format(self.choice_endpoint, text)
        request = RequestFactory().get(query)
        # Returns a list, so grab the first one.
        objs = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.filter(choice_text=text), objs)

        # Try with a votes query.
        votes = 928
        query = '{}?votes={}'.format(self.choice_endpoint, votes)
        request = RequestFactory().get(query)
        # Returns a list, so grab the first one.
        objs = Resource(request=request).resolve(request.path)
        self.assertItemsEqual(Choice.objects.filter(votes=votes), objs)
