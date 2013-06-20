# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import abc
import six
import string
import io
import collections
import mimeparse
from armet.exceptions import InvalidOperation


class Headers(collections.Mapping):
    """Describes a mapping abstraction over request headers.
    """

    @staticmethod
    def _Header(sequence, name):
        """Returns the passed header as a tuple.

        Implements a facade so that the response headers can override
        this to provide a mutable sequence header.
        """
        return tuple(sequence._headers.get(name, '').split(','))

    class _Sequence(dict):
        """
        Provides an implementation of a dictionary that retreives its
        values as sequences.
        """

        def __init__(self, headers):
            self._headers = headers

        def __missing__(self, name):
            self[name] = value = self.headers._Header(self, name)
            return value

    def __init__(self, obj):
        #! Reference to the request / response object.
        self._obj = obj

        #! Internal store of the multi-valued headers as lists.
        self._sequence = self._Sequence(self)

    @staticmethod
    def _normalize(name):
        """Normalizes the case of the passed name to be Http-Header-Case."""
        return str(string.capwords(name, '-'))

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

    def __init__(self, path, method, asynchronous, *args, **kwargs):
        #! The captured path of the request, after the mount point.
        #! Example: GET /api/poll/23 => '/23'
        self._path = path

        #! True if we're asynchronous.
        self._asynchronous = asynchronous

        #! The request headers dictionary.
        self._headers = self.Headers(self)

        # Build a dictionary of cookies from the request headers.
        self._cookies = {}
        cookies = self._headers.get('cookie')
        if cookies:
            for cookie in cookies.split(';'):
                name, value = cookie.strip().split('=')
                self._cookies[name] = value

        # Determine the actual HTTP method; apply the override header.
        override = self.headers.get('X-Http-Method-Override')
        if override:
            # Passed method was overriden; store override.
            self._method = override.upper()

        else:
            # Passed method is the actual method.
            self._method = method.upper()

        #! A reference to the bound resource; this is set in the resource
        #! view method after traversal.
        self._Resource = None

    @property
    def Resource(self):
        """Retrieves a reference to the bound resource object."""
        if self._Resource is None:
            raise InvalidOperation('Request object not bound to a resource.')

        return self._Resource

    @property
    def asynchronous(self):
        """True if we're being handled asynchronously."""
        return self._asynchronous

    @property
    def method(self):
        """Retrieves the HTTP upper-cased method of the request (eg. GET)."""
        return self._method

    @property
    def headers(self):
        """Retrieves the immutable request headers dictionary."""
        return self._headers

    @property
    def cookies(self):
        """Retrieves the immutable request headers dictionary."""
        return self._cookies

    @abc.abstractproperty
    def protocol(self):
        """Retrieves the upper-cased version of the protocol (eg. HTTP)."""

    @property
    def host(self):
        """Retrieves the hostname, normally from the `Host` header."""
        return self.headers.get('Host') or '127.0.0.1'

    @abc.abstractproperty
    def mount_point(self):
        """Retrieves the mount point portion of the path of this request."""

    @property
    def path(self):
        """Retrieves the path of the request, after the mount point."""
        return self._path

    @abc.abstractproperty
    def query(self):
        """Retrieves the text after the first ? in the path."""

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
    def _read(self, count=-1):
        """
        Read and return up to `count` bytes or characters (depending on
        the value of `self.encoding`).
        """

    def read(self, count=-1, deserialize=False, format=None):
        """
        Read and return up to `count` bytes or characters (depending on
        the value of `self.encoding`).

        @param[in] deserialize
            True to deserialize the resultant text using a determiend format
            or the passed format.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @note
            This is not the method that connectors will override; refer to
            `self._read` instead.
        """
        # Perform the initial read.
        content = self._read(count)

        if not content:
            # Content was empty; return an empty string.
            return ''

        if type(content) is six.binary_type:
            # If received a byte string; decode it.
            content = content.decode(self.encoding)

        if deserialize:
            # Deserialize the content using the passed format.
            content, _ = self.Resource.deserialize(content, self, format)

        # Whatever else we were passed; return it.
        return content

    @abc.abstractmethod
    def _readline(self, limit=-1):
        """Read and return one line from the stream."""

    def readline(self, limit=-1, deserialize=False, format=None):
        """Read and return one line from the stream.

        @param[in] deserialize
            True to deserialize the resultant text using a determiend format
            or the passed format.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @note
            This is not the method that connectors will override; refer to
            `self._readline` instead.
        """
        # Perform the initial read.
        content = self._readline(limit)

        if type(content) is six.binary_type:
            # If received a byte string; decode it.
            content = content.decode(self.encoding)

        if deserialize:
            # Deserialize the content using the passed format.
            content, _ = self.Resource.deserialize(content, self, format)

        # Whatever else we were passed; return it.
        return content

    @abc.abstractmethod
    def _readlines(self, hint=-1):
        """Read and return a list of lines from the stream."""

    def readlines(self, hint=-1, deserialize=False, format=None):
        """Read and return a list of lines from the stream.

        @param[in] deserialize
            True to deserialize the resultant text using a determiend format
            or the passed format.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @note
            This is not the method that connectors will override; refer to
            `self._readlines` instead.
        """
        # Perform the initial read; iterate through its lines.
        content = self._readlines(hint)
        for index, value in content:
            if type(value) is six.binary_type:
                # If received a byte string; decode it.
                value = value.decode(self.encoding)

                if deserialize:
                    # Deserialize the content using the passed format.
                    value, _ = self.Resource.deserialize(value, self, format)

                # Mutate the line list.
                content[index] = value

        # Return our decoded content.
        return content

    def deserialize(self, format=None):
        """Deserializes the request body using a determined deserializer.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @returns
            A tuple of the deserialized data and an instance of the
            deserializer used.
        """
        return self.Resource.deserialize(self.read(), self, format)

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
