from .base import RequestTest
from pytest import mark
from armet.resources import Resource


class TestAPI(RequestTest):

    @mark.bench("self.app.register")
    def test_register_name_with_resource_attribute(self):
        # Create an example resource to register in the API
        class FooResource:
            name = "bar"

        resource = FooResource

        self.app.register(resource)

        assert self.app._registry['bar'] is resource

    @mark.bench("self.app.register")
    def test_register_name_with_class_name(self):
        class FooResource:
            pass

        resource = FooResource

        self.app.register(resource)

        assert self.app._registry['foo'] is resource

    @mark.bench("self.app.register")
    def test_register_name_with_kwargs(self):
        class FooResource:
            pass

        resource = FooResource

        self.app.register(resource, name="bar")

        assert self.app._registry['bar'] is resource

    @mark.bench("self.app.__call__")
    def test_40x_exception_debug(self):

        self.app.debug = True

        response = self.get('/unknown-resource')

        assert response.status_code == 404

    @mark.bench("self.app.__call__")
    def test_internal_server_error(self):

        self.app.debug = True

        class TestResource(Resource):

            def read(self):
                raise Exception("This test raises an exception, and"
                                " prints to the console.")

        self.app.register(TestResource, name="test")

        response = self.get('/test')

        assert response.status_code == 500

    @mark.bench("self.app.__call__")
    def test_redirect_get(self):
        response = self.get('/get/')
        assert response.status_code == 301
        assert response.headers["Location"].endswith("/get")

    @mark.bench("self.app.__call__")
    def test_redirect_get_inverse(self):
        self.app.trailing_slash = True

        response = self.get('/get/')
        assert response.status_code == 404

        response = self.get('/get')
        assert response.status_code == 301

    @mark.bench("self.app.__call__")
    def test_redirect_post(self):
        response = self.post('/post/')
        assert response.status_code == 307
        assert response.headers["Location"].endswith("/post")

    @mark.bench("self.app.__call__")
    def test_no_content(self):

        class TestResource(Resource):

            def read(self):
                return None

        self.app.register(TestResource, name="test")

        response = self.get('/test')

        assert response.status_code == 204

    @mark.bench("self.app.__call__")
    def test_route(self):

        self.app.debug = True

        class TestResource(Resource):

            first_name = "Test"
            last_name = "Testerson"

            attributes = {'first_name', 'last_name'}

            def read(self):
                return {"first_name": self.first_name, "last_name": self.last_name}

        self.app.register(TestResource, name="test")

        response = self.get('/test')

        assert response.status_code == 200
