# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import httplib2
import unittest
import socket
import errno
import json
import base64
import six
from . import http

__all__ = [
    'http',
    'is_available',
    'skipUnlessAvailable',
    'Client',
    'ResourceTestCase'
]


def is_available(host='localhost', port=5000):
    try:
        httplib2.Http().request('http://{}:{}/'.format(host, port))
        return True

    except socket.error as ex:
        return ex.errno != errno.ECONNREFUSED


def skipUnlessAvailable(host='localhost', port=5000):
    if not is_available(host, port):
        raise unittest.SkipTest(
            'server is not available at {}:{}'.format(host, port))


class Client:

    def __init__(self, host='localhost', port=5000):
        # Set the default host and port.
        self.host = host
        self.port = port

        # Setup the HTTP/1.1 connection.
        self.connection = httplib2.Http()
        self.connection.follow_redirects = False

    def request(self, path='/', method='GET', body='', headers=None,
                url=None, username=None, password=None):
        if url is None:
            # Construct the URI.
            url = 'http://{}:{}{}'.format(self.host, self.port, path)

        # Default headers.
        if headers is None:
            headers = {}

        # Construct authorization if needed.
        if username or password:
            creds = '{}:{}'.format(username or '', password or '')
            creds = base64.b64encode(creds.encode('utf8'))
            headers['authorization'] = 'basic ' + creds.decode('utf8')

        # Serialize the body if neccessary.
        # TODO: Support more than JSON.
        if not isinstance(body, six.string_types):
            body = json.dumps(body)
            headers['content-type'] = 'application/json'

        # Perform the response. Remember this does not go anywhere; it is
        # caught by wsgi-intercept and mocked into Armet.
        return self.connection.request(
            url, method,
            body=body,
            headers=headers)

    def options(self, *args, **kwargs):
        kwargs.setdefault('method', 'OPTIONS')
        return self.request(*args, **kwargs)

    def head(self, *args, **kwargs):
        kwargs.setdefault('method', 'HEAD')
        return self.request(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault('method', 'POST')
        return self.request(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.setdefault('method', 'PUT')
        return self.request(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs.setdefault('method', 'DELETE')
        return self.request(*args, **kwargs)


class ResourceTestCase(unittest.TestCase):

    host = 'localhost'

    port = 5000

    def setUp(self):
        # Skip this test module unless the server is available.
        skipUnlessAvailable(self.host, self.port)

        # Initialize the test client.
        self.client = Client(self.host, self.port)
