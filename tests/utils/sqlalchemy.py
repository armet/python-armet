# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
import six
import os
import json


def _model_from_table(base, name):
    """Retreives the model class from the table name."""
    for _, cls in six.iteritems(base._decl_class_registry):
        if (isinstance(cls, type) and issubclass(cls, base) and
                cls.__table__.name == name):
            return cls


def load(filename, base, engine):
    """Loads the passed fixture into the database."""
    with open(filename, 'rb') as stream:
        # Read the binary data into text
        content = stream.read().decode('utf-8')

    # Decode the data as JSON
    data = json.loads(content)

    # Instantiate a session.
    from sqlalchemy.orm import Session
    session = Session(bind=engine)

    # Iterate through the entries to add them one by one.
    for item in data:
        # Resolve model from the table reference.
        model = _model_from_table(base, item['table'])

        # Check if the model exists.
        pk = item['columns'][item['pk']]
        compare = getattr(model, item['pk']) == pk
        instance = session.query(model).filter(compare).first()
        new = False
        if instance is None:
            # Instantiate the model object.
            instance = model()

            # Set it as new.
            new = True

            # Add the model to the session
            session.add(instance)

        # Iterate through the fields and set them on the model object.
        for name, value in six.iteritems(item['columns']):
            setattr(instance, name, value)

        if new:
            # Add it to the session.
            session.add(instance)

    # Commit the session to the database.
    session.commit()


def initialize():
    # Initialize the test database.
    from ..sqlalchemy import models
    models.Base.metadata.create_all(models.engine)

    # Install the fixture.
    fixture = os.path.dirname(__file__)
    fixture = os.path.join(
        fixture, '..', 'sqlalchemy', 'fixtures', 'initial_data.json')
    load(fixture, models.Base, models.engine)
