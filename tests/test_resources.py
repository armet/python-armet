import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base
import pytest


class SQLAlchemyTestBase:

    @pytest.fixture(autouse=True, scope="function")
    def sqlalchemy_session(self, request):
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:')
        self.Base = declarative_base()
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)

        self.Base.metadata.create_all(self.engine)
        self.session = self.Session()


class TestSqlalchemyResource(SQLAlchemyTestBase):
    pass
