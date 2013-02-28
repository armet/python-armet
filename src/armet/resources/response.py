# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division


class Response(object):
    """Implements the RESTful response abstraction.
    """

    def __init__(self, status=None):
        if status is not None:
            self.status = status

    @property
    def status(self):
        """Gets the status code of the response."""
        raise NotImplemented()

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""
        raise NotImplemented()

    def header(self, name, *args):
        """Sets a header with the passed name or gets the value of it."""
        raise NotImplemented()
