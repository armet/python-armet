# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import abc
import six
import collections


class Headers(collections.Mapping):
    """Describes a mapping abstraction over request and response headers.
    """

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to retrieve.
        """

    @abc.abstractmethod
    def __len__(self):
        """Retrieves the number of headers in the request."""

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterable for all headers in the request."""

    @abc.abstractmethod
    def __contains__(self, name):
        """Tests if the passed header exists in the request."""

    def getlist(self, name):
        """Retrieves a multi-valued header as a tuple of its values."""
        return self.get(name, '').split(',')


class Request(six.with_metaclass(abc.ABCMeta)):
    """Describes the RESTful request abstraction.
    """

    def __init__(self, path, method, headers, *args, **kwargs):
        #! The captured path of the request, after the mount point.
        #! Example: GET /api/poll/23 => '/23'
        self.__path = path

        #! The request headers dictionary.
        self.__headers = headers

        # Determine the actual HTTP method; apply the override header.
        override = self.headers.get('X-Http-Method-Override')
        if override:
            # Passed method was overriden; store override.
            self.__method = override.upper()

        else:
            # Passed method is the actual method.
            self.__method = method.upper()

    @property
    def method(self):
        """Retrieves the HTTP upper-cased method of the request (eg. GET)."""
        return self.__method

    @property
    def headers(self):
        """Retrieves the immutable request headers dictionary."""
        return self.__headers

    @property
    def path(self):
        """Retrieves the path of the request, after the mount point."""
        return self.__path

    @abc.abstractproperty
    def url(self):
        """Returns the complete URL of the request."""
