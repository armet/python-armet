#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import argparse
import os
import sys


#! Hostname at which to run the servers at.
HOST = 'localhost'


#! Port at which to run the servers at.
PORT = 5000


def initialize(name):
    if name.endswith('django'):
        # Ensure the settings are pointed to correctly.
        if not name.startswith('django'):
            # Unless django is being used for the http connector as well
            # there is only one settings file.
            name = 'django'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.{}.settings'.format(name)

        # Initialize the database tables and install the test fixtures.
        from django.core.management import call_command
        call_command('syncdb', verbosity=False, interactive=False)


def run(name):
    # Initialize the data access layer.
    initialize(name)

    # Let the world know.
    print('Armet version 0.3.0-pre\n'
          'Development server is running at http://localhost:5000/\n'
          'Quit the server with CONTROL-C.')

    # Initialize the request / response layer.
    if name.startswith('django'):
        # Ensure the settings are pointed to correctly.
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.{}.settings'.format(name)

        # Run the development server.
        from django.core.servers import basehttp
        basehttp.run(HOST, PORT, basehttp.get_internal_wsgi_application())

    elif name.startswith('flask'):
        # Run the development server.
        from tests.flask_django import app
        app.application.run(HOST, PORT)


def shell(name):
    # Initialize the data access layer.
    initialize(name)

    # Open the database access shell.
    if name.endswith('django'):
        from django.core.management import call_command
        call_command('shell_plus')


if __name__ == '__main__':
    # Extend our python path with armet.
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

    # Initialize and add arguments to the argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument('connector')
    parser.add_argument('command', choices=('run', 'shell'))

    # Parse the arguments using our parser.
    arguments = parser.parse_args()

    # Expand shorthands.
    connector = arguments.connector.replace('-', '_')
    if connector == 'django':
        connector = 'django_django'

    try:
        # Run the appropriate command.
        globals()[arguments.command](connector)

    except KeyboardInterrupt:
        # Closing the connection.
        pass
