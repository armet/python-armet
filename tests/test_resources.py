import pytest
import armet
import sqlalchemy as sa


@pytest.fixture(autouse=True, scope="function")
def User(db):
    class UserModel(db.Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode, nullable=False, default='')

    db.create_all()
    return UserModel


@pytest.fixture(autouse=True, scope="function")
def users_fixture(request, db, User, session):
    # 10 users.
    request.instance.names = names = [
        'joe', 'jerry', 'jon', 'jane', 'jim',
        'jack', 'jeff', 'jay', 'james', 'johansen']

    for name in names:
        session.add(User(name=name))

    session.commit()


@pytest.mark.usefixtures('users_fixture')
class TestSqlalchemyResource:

    @pytest.fixture(autouse=True)
    def setup_resource(self, User, db, http):
        class UserResource(armet.resources.SQLAlchemyResource):
            model = User
            session = db.Session
            slug_attribute = 'id'
            attributes = {'id', 'name'}

        http.app.register(UserResource, name='test')

    def test_read_all_success(self, http):
        response = http.get('/test')

        assert response.status_code == 200

    def test_read_all_return_all_data(self, http):
        response = http.get('/test')

        assert response.status_code == 200

        assert len(response.json) == 10

    def test_read_item_uses_slug_attribute(self, http):
        slugs = range(1, len(self.names) + 1)

        responses = [http.get('/test/{}'.format(x)) for x in slugs]

        http.app.debug = True

        for response, slug in zip(responses, slugs):
            assert response.status_code == 200

            assert response.json['id'] == slug
