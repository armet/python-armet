from django.test.client import RequestFactory
from armet import http
from armet.utils import test
from armet.resources import Resource


class Resolve(Resource):
    pass


class ResolveTestCase(test.TestCase):

    def setUp(self):
        self.endpoint = '/poll/4'

    def test_resolve(self):
        request = RequestFactory().resolve(self.endpoint)
        response = Resolve.view(request)
