# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import abc
import six
import io
import collections
import mimeparse


class Headers(collections.Mapping):
    """Describes a mapping abstraction over request headers.
    """

    class __Sequence(dict):
        """
        Provides an implementation of a dictionary that retreives its
        values as sequences.
        """

        def __init__(self, headers):
            self._headers = headers

        def __missing__(self, name):
            self[name] = value = tuple(self._headers.get(name, '').split(','))
            return value

    def __init__(self):
        self.__sequence = Headers.__Sequence(self)

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

    def index(self, name, value):
        """
        Return the index in the list of the first item whose value is x in
        the values of the named header.
        """
        return self.__sequence[name].index(value)

    def count(self, name, value):
        """
        Return the number of times a value appears in the list of the values
        of the named header.
        """
        return self.__sequence[name].count(value)

    def getlist(self, name):
        """Retrieves the passed header as a tuple of its values."""
        return self.__sequence[name]


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

    @abc.abstractproperty
    def protocol(self):
        return self.__handle.protocol.upper()

    @abc.abstractproperty
    def host(self):
        return self.__handle.host

    @property
    def path(self):
        """Retrieves the path of the request, after the mount point."""
        return self.__path

    @abc.abstractproperty
    def query(self):
        return self.__handle.query

    @abc.abstractproperty
    def uri(self):
        """Returns the complete URI of the request."""

    def close(self):
        """Request streams cannot be closed."""
        raise io.UnsupportedOperation()

    def closed(self):
        """True if the stream is closed."""
        return False

    def isatty(self):
        """Return True if the stream is interactive."""
        return False

    def readable(self):
        """Return True if the stream can be read from."""
        return True

    def writable(self):
        """Return True if the stream supports writing."""
        return False

    def seekable(self):
        """Return True if the stream supports random access."""
        return False

    @property
    def encoding(self):
        """
        The name of the encoding used to decode the stream’s bytes
        into strings, and to encode strings into bytes.

        Reads the charset value from the `Content-Type` header, if available;
        else, returns nothing.
        """
        # Get the `Content-Type` header, if available.
        content_type = self.headers.get('Content-Type')
        if content_type:
            # Parse out the primary type and parameters from the media type.
            ptype, _, params = mimeparse.parse_mime_type(content_type)

            # Return the specified charset or the default depending on the
            # primary type.
            default = 'utf-8' if ptype == 'application' else 'iso-8859-1'
            return params.get('charset', default)

    @abc.abstractmethod
    def read(self, count=None):
        """
        Read and return up to `count` bytes or characters (depending on
        the value of `self.encoding`).
        """

    @abc.abstractmethod
    def readline(self, limit=-1):
        """Read and return one line from the stream."""

    @abc.abstractmethod
    def readlines(self, hint=-1):
        """Read and return a list of lines from the stream."""
