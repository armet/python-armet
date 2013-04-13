# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import collections
import abc


__all__ = ['Response']


class Response(collections.MutableMapping):
    """Implements the RESTful response abstraction.
    """

    def __init__(self, status=None):
        if status is not None:
            self.status = status

    @abc.abstractproperty
    def status(self):
        """Gets the status code of the response."""

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""

    @abc.abstractproperty
    def content(self):
        """Gets the content of the response."""

    @content.setter
    def content(self, value):
        """Sets the content of the response."""

    @abc.abstractmethod
    def __getitem__(self, name):
        """Sets a header with the passed name."""

    @abc.abstractmethod
    def __setitem__(self, name, value):
        """Sets a header with the passed name."""

    @abc.abstractmethod
    def __delitem__(self, name):
        """Removes a header with the passed name."""

    @abc.abstractmethod
    def __len__(self):
        """Retrieves the number of headers in this response."""

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterable for all headers in this response."""

    def __contains__(self, name):
        """Tests if the passed header exists in the response object."""
