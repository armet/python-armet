# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from __future__ import print_function


def setup():
    # Initialize the database access layer
    from ..utils import sqlalchemy
    sqlalchemy.initialize()


def teardown():
    # Nothing really needs to be done for teardown
    pass
