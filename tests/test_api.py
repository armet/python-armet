from .base import RequestTest
from armet.resources import Resource
from armet import encoders, decoders
from unittest import mock
from pytest import mark


class TestAPI(RequestTest):

    @mark.xfail
    def test_route_resource(self):
        # Create and register some resources. to test api routing.
        retval = [{'foo': 'bar'}]

        route_resource = mock.Mock(name='route_resource')
        get_resource = mock.Mock(name='get_resource')
        route_resource().route.return_value = retval
        get_resource().read.return_value = retval

        self.app.register(route_resource, name='route')
        self.app.register(get_resource, name='read')

        response = self.get('/read')
        assert response.status_code == 200
        assert get_resource().read.called

        response = self.get('/route')
        assert response.status_code == 200
        assert route_resource().read.called

    def test_internal_server_error_raises_500(self):
        dead_resource = mock.Mock()
        dead_resource().read.side_effect = ValueError('DeadResourceException!')

        self.app.register(dead_resource, name='test')

        response = self.get('/test')
        assert response.status_code == 500
        assert dead_resource().read.called

    def test_redirect_get(self):
        response = self.get('/get/')
        assert response.status_code == 301
        assert response.headers["Location"].endswith("/get")

    def test_redirect_get_inverse(self):
        self.app.trailing_slash = True

        response = self.get('/get/')
        assert response.status_code == 404

        response = self.get('/get')
        assert response.status_code == 301

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

        assert response.status_code == 204
