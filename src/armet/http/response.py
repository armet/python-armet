# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import abc
import six
import re
import io
from armet import exceptions


class Headers(collections.MutableMapping):
    """Describes a mutable mapping abstraction over response headers.
    """

    class __Header(collections.MutableSequence):
        """
        Provides an implementation of a mutable sequence of multi-valued
        headers that are synced with the normal list of headers.
        """

        def __init__(self, sequence, name):
            #! Internal reference to the first-degree headers dictionary.
            self._headers = sequence._headers
            self._resource = sequence._resource
            self._name = name

            #! Internal store of the value at instantiation of the header.
            self._value = self._headers.get(self._name, '')

            #! Internal sequence of the list of the values of the header.
            self._sequence = self._value.split(',')

        def _pull(self):
            # Pull the headers from the source.
            if self._value != self._headers.get(name, ''):
                # If the header value has changed; update our sequence.
                self._value = self._headers.get(name, '')
                self._sequence = self._value.split(',')

        def __getitem__(self, index):
            # Retrieve the header value at the passed index.
            self._pull()
            return self._sequence[index]

        def __len__(self):
            self._pull()
            return len(self._sequence)

        def _push(self):
            # Push the headers to the source.
            self._value = ','.join(self._sequence)
            self._headers[self._name] = self._value

        def __setitem__(self, index, value):
            # Store the value at the passed index
            self._resource._assert_state()
            self._sequence[index] = value
            self._push()

        def __delitem__(self, index):
            # Remove the value at the passed index.
            self._resource._assert_state()
            del self._sequence[index]
            self._push()

        def insert(self, index, value):
            # Insert the header value at the passed index.
            self._resource._assert_state()
            self._sequence.insert(index, value)
            self._push()

    class __Sequence(dict):
        """
        Provides an implementation of a dictionary that retreives its
        values as sequences.
        """

        def __init__(self, headers, resource):
            self._headers = headers
            self._resource = resource

        def __missing__(self, name):
            self[name] = value = Headers.__Header(self, name)
            return value

    def __init__(self, resource):
        #! Internal store of the multi-valued headers as lists.
        self.__sequence = Headers.__Sequence(self, resource)

    @staticmethod
    def _normalize(name):
        """Normalizes the case of the passed name to be Http-Header-Case."""
        return '-'.join(x.capitalize() for x in re.split(r'_|-', name))

    @abc.abstractmethod
    def __getitem__(self, name):
        """Retrieves a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to retrieve.
        """

    @abc.abstractmethod
    def __setitem__(self, name, value):
        """Stores a header with the passed name.

        @param[in] name
            The name to store the header as. This is passed through
            `Headers.normalize` before storing on the response.

        @param[in] value
            The value to store for the header; for multi-valued headers,
            this can be a comma-separated list of values.
        """

    @abc.abstractmethod
    def __delitem__(self, name):
        """Removes a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to remove
            from the response.
        """

    @abc.abstractmethod
    def __len__(self):
        """Retrieves the number of headers in the response."""

    @abc.abstractmethod
    def __iter__(self):
        """Returns an iterable for all headers in the response."""

    @abc.abstractmethod
    def __contains__(self, name):
        """Tests if the passed header exists in the response."""

    def append(self, name, value):
        """Add a value to the end of the list for the named header."""
        return self.__sequence[name].append(value)

    def extend(self, name, values):
        """Extend the list for the named header by appending all values."""
        return self.__sequence[name].extend(values)

    def insert(self, name, index, value):
        """Insert a value at the passed index in the named header."""
        return self.__sequence[name].insert(index, value)

    def remove(self, name, value):
        """
        Remove the first item with the passed value from the
        list for the named header.
        """
        return self.__sequence[name].remove(value)

    def popvalue(self, name, index=None):
        """Remove the item at the given position in the named header list."""
        return self.__sequence[name].pop(index)

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

    def sort(self, name):
        """Sort the items of the list, in place."""
        return self.__sequence[name].sort()

    def reverse(self, name):
        """Reverse the elements of the list, in place."""
        return self.__sequence[name].reverse()

    def getlist(self, name):
        """Retrieves the passed header as a sequence of its values."""
        return self.__sequence[name]


class Response(six.with_metaclass(abc.ABCMeta)):
    """Describes the RESTful response abstraction.
    """

    def __init__(self, headers, *args, **kwargs):
        #! The response headers dictionary.
        self.__headers = headers

    def _assert_state(self):
        # Ensure things are not changed on a closed or streaming response.
        if self.closed or self.streaming:
            raise exceptions.InvalidOperation(
                'Resource is closed or streaming.')

    @property
    def headers(self):
        """Retrieves the response headers dictionary."""
        return self.__headers

    @abc.abstractproperty
    def status(self):
        """Gets the status code of the response."""

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""

    def isatty(self):
        """Return True if the stream is interactive."""
        return False

    def readable(self):
        """Return True if the stream can be read from."""
        return False

    def writable(self):
        """Return True if the stream supports writing."""
        return True

    def seekable(self):
        """Return True if the stream supports random access.

        @note
            Response objects do not support random access. However, python
            dictates that if this returns `False`, `self.tell()` must throw
            an `IOError`. So this returns `True` and both `seek` and
            `truncate` throw IOError.
        """
        return True

    def seek(self, *args, **kwargs):
        """Response objects do not support random access."""
        raise io.UnsupportedOperation()

    def truncate(self, *args, **kwargs):
        """Response objects do not support random access."""
        raise io.UnsupportedOperation()

    @abc.abstractmethod
    def close(self):
        """Flush and close the stream."""

    @abc.abstractproperty
    def closed(self):
        """True if the stream is closed."""

    @abc.abstractmethod
    def tell(self):
        """Return the current stream position."""

    @abc.abstractmethod
    def write(self, content):
        """Writes the given content to the output buffer.

        @param[in] content
            Either a byte array, a unicode string, or a generator. If `content`
            is a generator then calling `self.write(<generator>)` is
            equivalent to:

            @code
                for x in <generator>:
                    self.write(x)
                    self.flush()
            @endcode
        """

    def writelines(self, lines):
        """
        Write a list of lines to the stream.
        Line separators are not added.
        """
        for line in lines:
            self.write(line)

    @abc.abstractmethod
    def flush(self):
        """Flush the write buffers of the stream.

        This results in writing the current contents of the write buffer to
        the transport layer, initiating the HTTP/1.1 response. This initiates
        a streaming response. If the `Content-Length` header is not given
        then the chunked `Transfer-Encoding` is applied.
        """

    @abc.abstractproperty
    def streaming(self):
        """True if the stream is currently streaming content to the client.

        A response object is considered `streaming` directly after the
        first invocation of `flush`. When a response object
        becomes `streaming`, the `response` object may only be written to.
        Any attempt to modify the headers or the status of the response
        will result in a `TypeError`.
        """
