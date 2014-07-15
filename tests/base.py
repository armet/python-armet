from armet import api
import werkzeug.test
from pytest import fixture
import json


class MyResponse(werkzeug.Response):

    @property
    def json(self):
        return json.loads(self.data.decode('utf-8'))


class RequestTest:

    def request(self, path, **kwargs):
        # method and path are required arguments for sanity checking
        # purposes.

        # By default, use json.
        headers = kwargs.get('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept', 'application/json')

        environ = werkzeug.test.create_environ(
            path=path,
            **kwargs)

        return self.client.open(environ)

    # Helper functions!
    def get(self, *args, **kwargs):
        return self.request(*args, method='GET', **kwargs)

    def post(self, *args, **kwargs):
        return self.request(*args, method='POST', **kwargs)

    def put(self, *args, **kwargs):
        return self.request(*args, method='PUT', **kwargs)

    def delete(self, *args, **kwargs):
        return self.request(*args, method='DELETE', **kwargs)

    @fixture(autouse=True, scope="function")
    def fixture_api(self, request):
        inst = request.instance
        inst.app = api.Api()
        inst.client = werkzeug.test.Client(inst.app, MyResponse)
