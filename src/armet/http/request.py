# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import collections


__all__ = ['Request']


class Request(collections.Mapping):
    """Implements the RESTful request abstraction.
    """

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name."""

    @abc.abstractmethod
    def __len__(self, name):
        """Retrieves the number of headers in this request."""

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterable for all headers in this request."""

    def __contains__(self, name):
        """Tests if the passed header exists in the request object."""

    @abc.abstractproperty
    def url(self):
        """Returns the complete URL of the request."""

    @abc.abstractproperty
    def path(self):
        """Retrieves the path (after the mount point) of the request."""

    @path.setter
    def path(self, value):
        """Sets the path value of the request."""

    @abc.abstractproperty
    def method(self):
        """Retrieves the method of the request.

        This must account for X-Http-Method-Override header, if set.
        """
