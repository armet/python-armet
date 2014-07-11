from .base import RequestTest
from pytest import mark
from armet.resources import Resource
from armet.api import Api


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
                return [self.first_name, self.last_name]

        self.app.register(TestResource, name="test")
        self.app.register(TestResource, name="test2")

        response = self.get('/test/first_name/test2')

        assert response.status_code == 200

    def test_add_subapi(self):

        class PersonalApi(Api):
            pass

        class SubResource(Resource):
            attributes = {'success'}

            def read(self):
                return [{'success': True}]

        # Assert that all methods of accessing an api via name work.
        apis = [
            (Api(expose=True), {'name': 'test'}),
            (Api(expose=True, name='new_test'), {}),
            (PersonalApi(expose=True), {}),
        ]

        for api, kwargs in apis:
            api.register(SubResource, name='endpoint')
            self.app.register_api(api, **kwargs)

        # import ipdb; ipdb.set_trace()
        assert self.get('/test/endpoint').status_code == 200
        assert self.get('/new_test/endpoint').status_code == 200
        assert self.get('/personal/endpoint').status_code == 200
