# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from importlib import import_module
from wsgi_intercept.httplib2_intercept import install
import pytest
import armet
from armet import test


class BaseResourceTest(object):

    #! Host at which the intercept hook is installed.
    host = 'localhost'

    #! Port at which the intercept hook is installed.
    port = 5000

    @classmethod
    def setup_class(cls):
        # Initialize the test client.
        cls.client = test.Client(cls.host, cls.port)

    @pytest.fixture(autouse=True)
    def initialize(self, request, connectors):
        # Install the WSGI interception layer.
        install()

        # Remove the armet resources module so the resources
        # may be re-initialized.
        if 'tests.connectors.resources' in sys.modules:
            del sys.modules['tests.connectors.resources']

        # Initialize armet configuration.
        armet.use(connectors=connectors, debug=True)

        # Initialize the http access layer.
        prefix = 'tests.connectors.'
        http = import_module(prefix + connectors['http'])
        http.setup(connectors, self.host, self.port)

        # Add a finalizer to teardown the http layer.
        request.addfinalizer(lambda: http.teardown(self.host, self.port))

        if 'model' in connectors:
            # Initialize the database access layer.
            model = import_module(prefix + connectors['model'])
            model.setup()
