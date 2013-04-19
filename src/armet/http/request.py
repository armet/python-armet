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

    class _Sequence(dict):
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
        self._sequence = Headers._Sequence(self)

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
        return self._sequence[name].index(value)

    def count(self, name, value):
        """
        Return the number of times a value appears in the list of the values
        of the named header.
        """
        return self._sequence[name].count(value)

    def getlist(self, name):
        """Retrieves the passed header as a tuple of its values."""
        return self._sequence[name]


class Request(six.with_metaclass(abc.ABCMeta, six.Iterator)):
    """Describes the RESTful request abstraction.
    """

    def __init__(self, path, method, headers, *args, **kwargs):
        #! The captured path of the request, after the mount point.
        #! Example: GET /api/poll/23 => '/23'
        self.__path = path

        #! The request headers dictionary.
        self._headers = headers

        # Determine the actual HTTP method; apply the override header.
        override = self.headers.get('X-Http-Method-Override')
        if override:
            # Passed method was overriden; store override.
            self._method = override.upper()

        else:
            # Passed method is the actual method.
            self._method = method.upper()

    @property
    def method(self):
        """Retrieves the HTTP upper-cased method of the request (eg. GET)."""
        return self._method

    @property
    def headers(self):
        """Retrieves the immutable request headers dictionary."""
        return self._headers

    @abc.abstractproperty
    def protocol(self):
        return self._handle.protocol.upper()

    @abc.abstractproperty
    def host(self):
        return self._handle.host

    @property
    def path(self):
        """Retrieves the path of the request, after the mount point."""
        return self.__path

    @abc.abstractproperty
    def query(self):
        return self._handle.query

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
    def read(self, count=-1):
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

    def __iter__(self):
        """File-like objects are implicitly iterators."""
        return self

    def __next__(self):
        """Iterate over the lines of the request."""
        line = self.readline()
        if line:
            return line
        raise StopIteration()

    def __len__(self):
        """Returns the length of the request body, if known."""
        length = self.headers.get('Content-Length')
        return int(length) if length else 0

    def __getitem__(self, name):
        """Retrieves a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to retrieve.
        """
        return self.headers[name]

    def get(self, name, default=None):
        """Retrieves a header with the passed name."""
        return self.headers.get(name, default)

    def getlist(self, name):
        """
        Retrieves a the multi-valued list of
        the header with the passed name.
        """
        return self.headers.getlist(name)

    def __contains__(self, name):
        """Tests if the passed header exists in the request."""
        return name in self.headers

    def keys(self):
        """Return a new view of the header names."""
        return self.headers.keys()

    def values(self):
        """Return a new view of the header values."""
        return self.headers.values()

    def items(self):
        """Return a new view of the headers."""
        return self.headers.items()

    if not six.PY3:
        def iterkeys(self):
            """Return a new view of the header names."""
            return self.headers.iterkeys()

        def itervalues(self):
            """Return a new view of the header values."""
            return self.headers.itervalues()

        def iteritems(self):
            """Return a new view of the headers."""
            return self.headers.iteritems()
