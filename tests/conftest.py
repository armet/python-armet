import pytest
import sqlalchemy as sa
from armet import api
import werkzeug.test
import json


class DB:

    def __init__(self):
        from sqlalchemy.ext.declarative import declarative_base

        self.engine = sa.create_engine('sqlite:///:memory:')
        self.Base = declarative_base()
        self.Session = sa.orm.sessionmaker(bind=self.engine)

    def create_all(self):
        self.Base.metadata.create_all(self.engine)


@pytest.fixture(scope="function")
def db():
    return DB()


@pytest.yield_fixture(scope='function')
def session(request, db):
    """Adds a sqlalchemy session object to the test."""
    request.instance.session = session = db.Session()

    yield request.instance.session

    session.rollback()
    session.close()


class MyResponse(werkzeug.Response):

    @property
    def json(self):
        return json.loads(self.data.decode('utf-8'))


class HTTP:
    def __init__(self):
        self.app = api.Api()
        self.client = werkzeug.test.Client(self.app, MyResponse)

    def request(self, path, **kwargs):
        # method and path are required arguments for sanity checking
        # purposes.

        # By default, use json.
        headers = kwargs.get('headers', {})
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept', 'application/json')

        environ = werkzeug.test.create_environ(
            path=path,
            **kwargs)

        return self.client.open(environ)

    # Helper functions!
    def get(self, *args, **kwargs):
        return self.request(*args, method='GET', **kwargs)

    def post(self, *args, **kwargs):
        return self.request(*args, method='POST', **kwargs)

    def put(self, *args, **kwargs):
        return self.request(*args, method='PUT', **kwargs)

    def delete(self, *args, **kwargs):
        return self.request(*args, method='DELETE', **kwargs)


@pytest.fixture(scope='function')
def http():
    return HTTP()
