from pytest import mark
from unittest import mock
from armet.resources import Resource
from armet.api import Api


class TestAPI:

    @mark.bench("http.app.register")
    def test_register_name_with_resource_attribute(self, http):
        # Create an example resource to register in the API
        class FooResource:
            name = "bar"

        resource = FooResource

        http.app.register(resource)

        assert http.app._registry.find(name='bar')[0] is resource

    @mark.bench("http.app.register")
    def test_register_name_with_class_name(self, http):
        class FooResource:
            pass

        resource = FooResource

        http.app.register(resource)

        assert http.app._registry.find(name='foo')[0] is resource

    @mark.bench("http.app.register")
    def test_register_name_with_kwargs(self, http):
        class FooResource:
            pass

        resource = FooResource

        http.app.register(resource, name="bar")

        assert http.app._registry.find(name='bar')[0] is resource

    @mark.bench("http.app.__call__")
    def test_40x_exception_debug(self, http):

        response = http.get('/unknown-resource')

        assert response.status_code == 404

    @mark.bench("http.app.__call__")
    def test_internal_server_error(self, http):

        class TestResource(Resource):

            def read(self):
                raise Exception("This test raises an exception, and"
                                " prints to the console.")

        http.app.register(TestResource, name="test")

        http.app.debug = True

        with mock.patch('traceback.print_exc') as mocked:
            response = http.get('/test')
            assert mocked.called

        assert response.status_code == 500

    @mark.bench("http.app.__call__")
    def test_redirect_get(self, http):
        response = http.get('/get/')
        assert response.status_code == 301
        assert response.headers["Location"].endswith("/get")

    @mark.bench("http.app.__call__")
    def test_redirect_get_inverse(self, http):
        http.app.trailing_slash = True

        response = http.get('/get/')
        assert response.status_code == 404

        response = http.get('/get')
        assert response.status_code == 301

    @mark.bench("http.app.__call__")
    def test_redirect_post(self, http):
        response = http.post('/post/')
        assert response.status_code == 307
        assert response.headers["Location"].endswith("/post")

    @mark.bench("http.app.__call__")
    def test_no_content(self, http):

        class TestResource(Resource):

            def read(self):
                return None

        http.app.register(TestResource, name="test")

        response = http.get('/test')

        assert response.status_code == 204

    @mark.bench("http.app.__call__")
    def test_route(self, http):

        class TestResource(Resource):

            relationships = {"test2"}

            def prepare(self, item):
                return item

            def read(self):
                return "data"

        class Test2Resource(Resource):

            def prepare(self, item):
                return item

            def read(self):
                return "data2"

        http.app.register(TestResource, name="test")
        http.app.register(Test2Resource, name="test2")

        response = http.get('/test/1/test2')

        assert response.status_code == 200
        assert response.data == b'["data2"]'

    def test_add_subapi(self, http):

        class PersonalApi(Api):
            pass

        class SubResource(Resource):
            attributes = {'success'}

            def read(self):
                return [{'success': True}]

        # Assert that all methods of accessing an api via name work.
        apis = [
            (Api(), {'name': 'test'}),
            (Api(name='new_test'), {}),
            (PersonalApi(), {}),
        ]

        for api, kwargs in apis:
            api.register(SubResource, name='endpoint')
            http.app.register(api, **kwargs)

        assert http.get('/test/endpoint').status_code == 200
        assert http.get('/new_test/endpoint').status_code == 200
        assert http.get('/personal/endpoint').status_code == 200

    def test_multiname_route_with_invalid_resource(self, http):
        """Test that we indeed get a 404 on a request with
        2+ "names", i.e /name/slug/name"""

        response = http.get('/name/slug/name')

        assert response.status_code == 404

    def test_get_on_root(self, http):
        response = http.get('/')

        assert response.status_code == 404

    def test_method_not_allowed(self, http):
        class FooResource(Resource):
            pass

        http.app.register(FooResource)

        response = http.request('/foo', method="GARBAGE")

        assert response.status_code == 405
