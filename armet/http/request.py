# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import abc
import six
import string
import io
import collections
import mimeparse
import weakref
from six.moves import http_cookies


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

    def __init__(self):
        #! Internal store of the multi-valued headers as lists.
        self._sequence = self._Sequence(self)

    @staticmethod
    def normalize(name):
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


class Request(six.Iterator):
    """Describes the RESTful request abstraction.
    """

    #! Dictionary-like interface to access headers; this should be
    #! set by the dervied class to an instance of a derived Headers class.
    headers = None

    def __init__(self, path, method, asynchronous, *args, **kwargs):
        #! The captured path of the request, after the mount point.
        #! Example: GET /api/poll/23 => '/23'
        self.path = path

        #! True if we're asynchronous.
        self.asynchronous = asynchronous

        # Determine the actual HTTP method; apply the override header.
        override = self.headers.get('X-Http-Method-Override')
        if override:
            # Passed method was overriden; store override.
            self.method = override.upper()

        else:
            # Passed method is the actual method.
            self.method = method.upper()

        #! Cookie jar full of python morsel objects that represent the
        #! cookies that were sent with the request.
        text = self.get('Cookie')
        self.cookies = http_cookies.SimpleCookie()
        if text:
            self.cookies.load(str(text))

        #! A reference to the bound resource; this is set in the resource
        #! view method after traversal.
        self._resource = None

    def bind(self, resource):
        """Binds this to the passed resource object.

        This is used so that the request and response classes can access
        metadata and configuration on the resource handling this request
        so helper methods on the request and response like `serialize` work
        in full knowledge of configuration supplied to the resource.
        """
        self._resource = weakref.proxy(resource)

    @property
    def resource(self):
        return self._resource

    @property
    def protocol(self):
        """Retrieves the upper-cased version of the protocol (eg. HTTP)."""
        raise NotImplementedError()

    @property
    def host(self):
        """Retrieves the hostname, normally from the `Host` header."""
        return self.headers.get('Host') or '127.0.0.1'

    @property
    def mount_point(self):
        """Retrieves the mount point portion of the path of this request."""
        raise NotImplementedError()

    @property
    def query(self):
        """Retrieves the text after the first ? in the path."""
        raise NotImplementedError()

    @property
    def uri(self):
        """Returns the complete URI of the request."""
        raise NotImplementedError()

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

    def _read(self):
        """Read and return the request data.

        @note Connectors should override this method.
        """
        return None

    def read(self, deserialize=False, format=None):
        """Read and return the request data.

        @param[in] deserialize
            True to deserialize the resultant text using a determiend format
            or the passed format.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.
        """

        if deserialize:
            data, _ = self.deserialize(format=format)
            return data

        content = self._read()

        if not content:
            return ''

        if type(content) is six.binary_type:
            content = content.decode(self.encoding)

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
        return self._resource.deserialize(self, format=format)

    def __len__(self):
        """Returns the length of the request body, if known."""
        length = self.headers.get('Content-Length')
        return int(length) if length else 0

    def __getitem__(self, name):
        """Retrieves a header with the passed name."""
        return self.headers[name]

    def get(self, name, default=None):
        """Retrieves a header with the passed name."""
        return self.headers.get(name, default)

    def getlist(self, name):
        """
        Retrieves a the multi-valued list of the header with
        the passed name.
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
