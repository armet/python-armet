from django.test.client import RequestFactory
from armet.utils import test
from armet.resources import Resource
from armet.tests.models import Poll


class Resolve(Resource):
    pass


class ResolveTestCase(test.TestCase):

    def setUp(self):
        super(ResolveTestCase, self).setUp()
        self.endpoint = '/poll/4'

    def test_resolve(self):
        """Test the resolvability of a url."""
        request = RequestFactory().get(self.endpoint)
        obj = Resolve(request=request).resolve(request.path)
        self.assertItemsEqual(Poll.objects.all(), obj)
