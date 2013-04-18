# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# Instantiate the declarative base.
Base = declarative_base()


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    question = Column(String)


# Instantiate the engine used to access said models.
# TODO: This should be configurable by a cfg file or other.
from sqlalchemy import create_engine
engine = create_engine('sqlite:///db.sqlite3')
