# -*- coding: utf-8 -*-
"""Normalizes access to the HTTP libraries.
"""
from __future__ import print_function, unicode_literals, division

# Normalize `http.client` and `httplib`.
from six.moves import http_client as client

try:
    # Attempt to get additional status codes (added in python 3.2)
    getattr(client, 'PERMANENT_REDIRECT')
    getattr(client, 'PRECONDITION_REQUIRED')
    getattr(client, 'TOO_MANY_REQUESTS')
    getattr(client, 'REQUEST_HEADER_FIELDS_TOO_LARGE')
    getattr(client, 'NETWORK_AUTHENTICATION_REQUIRED')

except AttributeError:
    # Don't have em; add them.
    client.PERMANENT_REDIRECT = 308
    client.PRECONDITION_REQUIRED = 428
    client.TOO_MANY_REQUESTS = 429
    client.REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    client.NETWORK_AUTHENTICATION_REQUIRED = 511

# Import request and response classes into the root level of the package.
from .request import Request
from .response import Response
