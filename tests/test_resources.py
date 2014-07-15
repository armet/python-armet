import pytest
import armet
from .base import RequestTest


@pytest.mark.usefixtures('users_fixture', 'request')
class TestSqlalchemyResource(RequestTest):

    @pytest.fixture(autouse=True)
    def setup_resource(self, User, db):
        class UserResource(armet.resources.SQLAlchemyResource):
            model = User
            session = db.Session
            slug_attribute = 'id'
            attributes = {'id', 'name'}

        self.app.register(UserResource, name='test')

    def test_read_all_success(self):
        response = self.get('/test')

        assert response.status_code == 200

    def test_read_all_return_all_data(self):
        response = self.get('/test')

        assert response.status_code == 200

        assert len(response.json) == 10

    def test_read_item_uses_slug_attribute(self):
        slugs = range(1, 11)

        responses = [self.get('/test/{}'.format(x)) for x in slugs]

        self.app.debug = True

        for response, slug in zip(responses, slugs):
            assert response.status_code == 200

            assert response.json['id'] == slug
