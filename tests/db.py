import pytest
import sqlalchemy as sa

# import ipdb; ipdb.set_trace()

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


@pytest.fixture(scope="function")
def User(db):
    class UserModel(db.Base):
        __tablename__ = 'user'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        name = sa.Column(sa.Unicode, nullable=False, default='')

    db.create_all()
    return UserModel


@pytest.fixture(scope="function")
def Box(db):
    class BoxModel(db.Base):
        __tablename__ = 'box'
        id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
        user_id = sa.Column(sa.ForeignKey(User.id), nullable=False)

    db.create_all()
    return BoxModel


@pytest.fixture(scope="function")
def users_fixture(db, User):
    session = db.Session()

    # 10 users.
    names = [
        'joe', 'jerry', 'jon', 'jane', 'jim',
        'jack', 'jeff', 'jay', 'james', 'johansen']

    for name in names:
        session.add(User(name=name))

    session.commit()
    session.close()
