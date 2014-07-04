from .base import RequestTest
from armet import encoders, decoders
from unittest import mock


class TestAPI(RequestTest):

    def setup(self):
        super().setup()

        # Register a dummy encoder and decoder.
        self.codec = mock.MagicMock()
        self.codec.return_value = b'test'
        encoders.register(self.codec, names=['test'], mime_types=['test/test'])
        decoders.register(self.codec, names=['test'], mime_types=['test/test'])

    def test_route_resource(self):
        # Create and register some resources. to test api routing.
        route_resource = mock.Mock(['route'], name='route_resource')
        get_resource = mock.Mock(['get'], name='get_resource')
        route_resource.route.return_value = {'foo': 'bar'}
        get_resource.get.return_value = {'foo': 'bar'}

        self.app.register(lambda request: route_resource, name='route')
        self.app.register(lambda request: get_resource, name='get')

        # Test routing to those resources.
        headers = {'Accept': 'test/test', 'Content-Type': 'test/test'}

        response = self.get('/get', headers=headers)
        assert response.status_code == 200
        assert get_resource.get.called

        response = self.get('/route', headers=headers)
        assert response.status_code == 200
        assert route_resource.route.called
