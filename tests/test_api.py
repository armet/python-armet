from .base import RequestTest
from armet.resources import Resource
from armet import encoders, decoders
from unittest import mock


class TestAPI(RequestTest):

    def setup(self):
        # Register a dummy encoder and decoder.
        self.codec = mock.MagicMock()
        self.codec.return_value = b'test'
        encoders.register(names=['test'], mime_types=['test/test'])(self.codec)
        decoders.register(names=['test'], mime_types=['test/test'])(self.codec)

    def test_route_resource(self):
        # Create and register some resources. to test api routing.
        route_resource = mock.Mock(name='route_resource')
        get_resource = mock.Mock(name='get_resource')
        route_resource.route.return_value = {'foo': 'bar'}
        get_resource.get.return_value = {'foo': 'bar'}

        self.app.register(lambda *a, **kw: route_resource, name='route')
        self.app.register(lambda *a, **kw: get_resource, name='get')

        # Test routing to those resources.
        headers = {'Accept': 'test/test', 'Content-Type': 'test/test'}

        response = self.get('/get', headers=headers)
        assert response.status_code == 200
        assert get_resource.read.called

        response = self.get('/route', headers=headers)
        assert response.status_code == 200
        assert route_resource.read.called

        # Unregistser resources
        del self.app._registry["route"]
        del self.app._registry["get"]

    def test_redirect_get(self):
        response = self.get('/get/')
        assert response.status_code == 301
        assert response.headers["Location"].endswith("/get")

    def test_redirect_get_inverse(self):
        trailing_slash = self.app.trailing_slash
        self.app.trailing_slash = True

        response = self.get('/get/')
        assert response.status_code == 404

        response = self.get('/get')
        assert response.status_code == 301

        self.app.trailing_slash = trailing_slash

    def test_redirect_post(self):
        response = self.post('/post/')
        assert response.status_code == 307
        assert response.headers["Location"].endswith("/post")

    def test_no_content(self):

        class TestResource(Resource):
            def read(self):
                return None

        self.app.register(TestResource, name="test")

        response = self.get('/test')

        import ipdb; ipdb.set_trace()
        assert response.status_code == 204

