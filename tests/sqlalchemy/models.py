# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


# Instantiate the declarative base.
Base = declarative_base()


class Poll(Base):
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    question = Column(String)
