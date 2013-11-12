# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import os
import json
import armet
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

# Instantiate the declarative base.
Base = declarative_base()

# Instantiate the engine used to access the models.
engine = sa.create_engine('sqlite:///:memory:')

# Construct the session factory.
Session = orm.sessionmaker(bind=engine)


class Poll(Base):

    __tablename__ = 'poll'

    id = sa.Column(sa.Integer, primary_key=True)

    question = sa.Column(sa.String(1024))

    available = sa.Column(sa.Boolean)

    votes = sa.Column(sa.Integer)


def _load_fixture(filename):
    """
    Loads the passed fixture into the database following the
    django format.
    """

    # Read the binary data into text
    with open(filename, 'rb') as stream:
        content = stream.read().decode('utf-8')

    # Decode the data as JSON
    data = json.loads(content)

    # Instantiate a session.
    session = Session()

    # Iterate through the entries to add them one by one.
    for item in data:
        # Resolve model from the table reference.
        table = Base.metadata.tables[item['model'].split('.')[-1]]

        # Add the primary key.
        item['fields']['id'] = item['pk']

        # Add a new row.
        session.connection().execute(table.insert().values(**item['fields']))

    # Commit the session to the database.
    session.commit()


def model_setup():
    # Initialize the database and create all models.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Load the data fixture.
    _load_fixture(os.path.join(os.path.dirname(__file__), 'data.json'))

    # Configure armet and provide the session factory.
    armet.use(Session=Session)
