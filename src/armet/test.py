# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import httplib2
import unittest
import socket
import errno


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
        self.host = host
        self.port = port

        self.connection = httplib2.Http()
        self.connection.follow_redirects = False

    def request(self, path='/', method='GET'):
        url = 'http://{}:{}{}'.format(self.host, self.port, path)
        return self.connection.request(url, method)


class TestCase(unittest.TestCase):

    def setUp(self):
        # Skip this test module unless the server is available.
        skipUnlessAvailable()

        # Initialize the test client.
        self.client = Client()
