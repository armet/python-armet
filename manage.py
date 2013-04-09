#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import argparse
import os
import sys
import contextlib


@contextlib.contextmanager
def redirect_output():
    stdout = sys.stdout
    sys.stdout = open(os.devnull, 'wb')
    yield None  # Executing the inner block.
    sys.stdout.close()
    sys.stdout = stdout


def run(connector):
    if connector.endswith('django'):
        # Ensure the settings are pointed to correctly.
        module = 'tests.{}.settings'.format(connector)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", module)

        # Initialize the database tables and install the test fixtures.
        from django.core.management import call_command
        with redirect_output():
            call_command('syncdb', skip_validation=True, interactive=False)
            call_command('loaddata', 'test', skip_validation=True)

    # Let the world know.
    print('Armet version 0.3.0-pre')
    print('Development server is running at http://127.0.0.1:5000/')
    print('Quit the server with CONTROL-C.')

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

    try:
        # Run the appropriate command.
        globals()[arguments.command](connector)

    except KeyboardInterrupt:
        # Closing the connection.
        pass
