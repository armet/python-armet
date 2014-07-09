from armet import api
import werkzeug.test


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

        # import ipdb; ipdb.set_trace()

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

    def setup_class(cls):
        cls.app = api.Api()
        cls.client = werkzeug.test.Client(cls.app, werkzeug.Response)
