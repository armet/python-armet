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

        assert self.app._registry.find(name='bar') is resource

    @mark.bench("self.app.register")
    def test_register_name_with_class_name(self):
        class FooResource:
            pass

        resource = FooResource

        self.app.register(resource)

        assert self.app._registry.find(name='foo') is resource

    @mark.bench("self.app.register")
    def test_register_name_with_kwargs(self):
        class FooResource:
            pass

        resource = FooResource

        self.app.register(resource, name="bar")

        assert self.app._registry.find(name='bar') is resource

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

            def prepare(self, item):
                return item

            def read(self):
                return "data"

        class Test2Resource(Resource):

            def prepare(self, item):
                return item

            def read(self):
                return "data2"

        self.app.register(TestResource, name="test")

        self.app.register(Test2Resource, name="test2")

        response = self.get('/test/1/test2')
        # Json serializer is broken?
        assert response.data == b'["data2"]'

        assert response.status_code == 200

    def test_multiname_route_with_invalid_resource(self):
        """Test that we indeed get a 404 on a request with
        2+ "names", i.e /name/slug/name"""

        response = self.get('/name/slug/name')

        assert response.status_code == 404

    def test_get_on_root(self):
        response = self.get('/')

        assert response.status_code == 404

    def test_method_not_allowed(self):
        class FooResource(Resource):
            pass

        self.app.register(FooResource)

        response = self.request('/foo', method="GARBAGE")

        assert response.status_code == 405
