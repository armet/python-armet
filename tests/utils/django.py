# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
import os


def initialize(package):
    # Setup the environment variables.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.{}.settings'.format(package)

    # Initialize the test database.
    from django.core.management import call_command
    call_command('syncdb', verbosity=False, interactive=False)

    # from django.db import connections, DEFAULT_DB_ALIAS
    # connection = connections[DEFAULT_DB_ALIAS]
    # connection.creation.create_test_db()
