#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import argparse
import os
import sys


class RedirectOutput:

    def __init__(self, stdout=None):
        self.stdout = self._stdout = stdout

    def __enter__(self):
        if self._stdout is None:
            self.stdout = open(os.devnull, 'w')

        self.old_stdout = sys.stdout
        self.old_stdout.flush()
        sys.stdout = self.stdout

    def __exit__(self, *args, **kwargs):
        self.stdout.flush()
        sys.stdout = self.old_stdout

        if self._stdout is None:
            self.stdout.close()


def run(connector):
    if connector.endswith('django'):
        # Ensure the settings are pointed to correctly.
        module = 'tests.{}.settings'.format(connector)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", module)

        # Initialize the database tables.
        with RedirectOutput():
            from django.db import connections, DEFAULT_DB_ALIAS
            connection = connections[DEFAULT_DB_ALIAS]
            connection.creation.create_test_db()

    if connector.startswith('django'):
        # Run the development server.
        from django.core.servers import basehttp
        application = basehttp.get_internal_wsgi_application()
        basehttp.run('localhost', 5000, application)


if __name__ == '__main__':
    # Extend our python path with armet.
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

    # Initialize and add arguments to the argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('connector', choices=(
        'django',
        'django_django',
        'flask'
    ))
    parser.add_argument('command', choices=('run', 'shell'))

    # Parse the arguments using our parser.
    arguments = parser.parse_args()

    # Expand shorthands.
    connector = arguments.connector
    if connector == 'django':
        connector = 'django_django'

    # Run the appropriate command.
    globals()[arguments.command](connector)
