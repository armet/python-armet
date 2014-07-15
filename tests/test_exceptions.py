from armet.http import exceptions
from armet.resources import Resource as BaseResource


class TestExceptions:

    def test_exception_contains_error_in_response(self, http):
        class ThrowingResource(BaseResource):
            def read(self):
                raise exceptions.BadRequest({'test': 'testing'})

        http.app.register(ThrowingResource, name='error')

        response = http.get('/error')

        assert response.status_code == 400
        assert response.json == {'test': 'testing'}
        assert response.headers['Content-Type'] == 'application/json'

    def test_500_error_has_no_content(self, http):
        class TypeErrorResource(BaseResource):
            def read(self):
                raise TypeError
        http.app.register(TypeErrorResource, name='error')
        return TypeErrorResource

        response = http.get('/error')

        assert response.status_code == 500
        assert response.headers['Content-Type'] == 'text/plain'
        assert len(response.data) == 0
