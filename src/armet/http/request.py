# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import collections


__all__ = ['Request']


class Request(collections.Mapping):
    """Implements the RESTful request abstraction.
    """

    def __init__(self, path, *args, **kwargs):
        #! The captured path of the request, after the mount point.
        #! Example: GET /api/poll/23 => '/23'
        self.path = path

        # Determine the actual HTTP method; apply the override header.
        override = self.get('X-Http-Method-Override')
        if override:
            self.method = override.upper()

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name.

        @param[in] name
            The name of the header to retrieve. Headers are retrieved
            case-insensitive.
        """

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
    def method(self):
        """Retrieves the method of the request."""

    @method.setter
    def method(self, value):
        """Set the method of the request."""
