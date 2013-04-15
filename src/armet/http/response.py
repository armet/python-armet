# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import collections
import abc


__all__ = ['Response']


class Response(collections.MutableMapping):
    """Implements the RESTful response abstraction.
    """

    @abc.abstractproperty
    def status(self):
        """Gets the status code of the response."""

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""

    def write(self, chunk):
        """Writes the chunk to the response."""

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
