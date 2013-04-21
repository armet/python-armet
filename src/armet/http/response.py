# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import abc
import six
import re
import mimeparse
import io
from armet import exceptions
from . import request


class Headers(collections.MutableMapping, request.Headers):
    """Describes a mutable mapping abstraction over response headers.
    """

    class _Header(collections.MutableSequence):
        """
        Provides an implementation of a mutable sequence of multi-valued
        headers that are synced with the normal list of headers.
        """

        def __init__(self, sequence, name):
            #! Internal reference to the first-degree headers dictionary.
            self._headers = sequence._headers
            self._obj = self._headers._obj
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
            self._obj._assert_open()
            self._sequence[index] = value
            self._push()

        def __delitem__(self, index):
            # Remove the value at the passed index.
            self._obj._assert_open()
            del self._sequence[index]
            self._push()

        def insert(self, index, value):
            # Insert the header value at the passed index.
            self._obj._assert_open()
            self._sequence.insert(index, value)
            self._push()

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

    def append(self, name, value):
        """Add a value to the end of the list for the named header."""
        return self._sequence[name].append(value)

    def extend(self, name, values):
        """Extend the list for the named header by appending all values."""
        return self._sequence[name].extend(values)

    def insert(self, name, index, value):
        """Insert a value at the passed index in the named header."""
        return self._sequence[name].insert(index, value)

    def remove(self, name, value):
        """
        Remove the first item with the passed value from the
        list for the named header.
        """
        return self._sequence[name].remove(value)

    def popvalue(self, name, index=None):
        """Remove the item at the given position in the named header list."""
        return self._sequence[name].pop(index)

    def sort(self, name):
        """Sort the items of the list, in place."""
        return self._sequence[name].sort()

    def reverse(self, name):
        """Reverse the elements of the list, in place."""
        return self._sequence[name].reverse()


class Response(six.with_metaclass(abc.ABCMeta)):
    """Describes the RESTful response abstraction.
    """

    def __init__(self, asynchronous, *args, **kwargs):
        #! The response headers dictionary.
        self._headers = self.Headers(self)

        #! True if the response object is closed.
        self._closed = False

        #! True if the response object is streaming.
        self._streaming = False

        #! True if we're asynchronous.
        self._asynchronous = asynchronous

    def _assert_open(self):
        self._assert_not_closed()
        if self.streaming:
            raise exceptions.InvalidOperation('Response is streaming.')

    def _assert_not_closed(self):
        if self.closed:
            raise exceptions.InvalidOperation('Response is closed.')

    @property
    def headers(self):
        """Retrieves the response headers dictionary."""
        return self._headers

    @property
    def asynchronous(self):
        """True if we're being handled asynchronously."""
        return self._asynchronous

    @abc.abstractproperty
    def status(self):
        """Gets the status code of the response."""

    @status.setter
    def status(self, value):
        """Sets the status code of the response.
        """

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

    @property
    def encoding(self):
        if hasattr(self, '__encoding'):
            # Encoding has been set manually.
            return self.__encoding

        # Get the `Content-Type` header, if available.
        content_type = self.headers.get('Content-Type')
        if content_type:
            # Parse out the primary type and parameters from the media type.
            ptype, _, params = mimeparse.parse_mime_type(content_type)

            # Return the specified charset or the default depending on the
            # primary type.
            default = 'utf-8' if ptype == 'application' else 'iso-8859-1'
            return params.get('charset', default)

        # No encoding found.

    @encoding.setter
    def encoding(self, value):
        # Explicitly set the character encoding to use.
        self.__encoding = value

    @abc.abstractmethod
    def close(self):
        """Flush and close the stream.
        """
        # We can't close the stream if we're already closed.
        self._assert_not_closed()

        if self.streaming or self.asynchronous:
            # We're streaming or asynchronous; flush out the current buffer.
            self.flush()

        else:
            # We're not streaming, auto-write content-length if not
            # already set.
            if 'Content-Length' not in self.headers:
                self.headers['Content-Length'] = self.tell()

        # We're done with the response; inform the HTTP connector
        # to close the response stream.
        self._closed = True

    @property
    def closed(self):
        """True if the stream is closed."""
        return self._closed

    @abc.abstractmethod
    def tell(self):
        """Return the current stream position."""

    @abc.abstractmethod
    def _write(self, chunk):
        """Writes the given byte string chunk to the output buffer.
        """

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

        @note
            This is not the method that connectors will override; refer to
            `self._write` instead.
        """
        # Ensure we do not write a closed response.
        self._assert_not_closed()

        if content is None:
            # There is nothing here..
            return

        if type(content) is six.binary_type:
            # If passed a byte string we can optionally encode it and
            # write it to the stream
            if self.encoding:
                content = content.encode(self.encoding)
            self._write(content)

        elif isinstance(content, six.string_types):
            # If passed a string, we hope that the user
            # encoded it properly.
            self._write(content)

        else:
            try:
                # If passed some kind of iterator, attempt to recurse into
                # oblivion.
                for chunk in content:
                    self.write(chunk)

            except TypeError:
                # Apparently we didn't get an iterator..
                # Try and blindly cast this into a byte string and
                # just write it.
                self.write(six.binary_type(content))

    def writelines(self, lines):
        """
        Write a list of lines to the stream.
        Line separators are not added.
        """
        for line in lines:
            self.write(line)

    @abc.abstractmethod
    def _flush(self):
        """Flush the write buffers of the stream."""

    def flush(self):
        """Flush the write buffers of the stream.

        This results in writing the current contents of the write buffer to
        the transport layer, initiating the HTTP/1.1 response. This initiates
        a streaming response. If the `Content-Length` header is not given
        then the chunked `Transfer-Encoding` is applied.

        @note
            This is not the method that connectors will override; refer to
            `self._flush` instead.
        """
        self._assert_not_closed()
        self._flush()
        self._streaming = True

    @property
    def streaming(self):
        """True if the stream is currently streaming content to the client.

        A response object is considered `streaming` directly after the
        first invocation of `flush`. When a response object
        becomes `streaming`, the `response` object may only be written to.
        Any attempt to modify the headers or the status of the response
        will result in a `TypeError`.
        """
        return self._streaming

    def __getitem__(self, name):
        """Retrieves a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to retrieve.
        """
        return self._headers[name]

    def __setitem__(self, name, value):
        """Stores a header with the passed name.

        @param[in] name
            The name to store the header as. This is passed through
            `Headers.normalize` before storing on the response.

        @param[in] value
            The value to store for the header; for multi-valued headers,
            this can be a comma-separated list of values.
        """
        self._headers[name] = value

    def __delitem__(self, name):
        """Removes a header with the passed name.

        @param[in] name
            The case-insensitive name of the header to remove
            from the response.
        """
        del self._headers

    def __len__(self):
        """Retrieves the actual length of the response."""
        return self.tell()

    def __contains__(self, name):
        """Tests if the passed header exists in the response."""
        return name in self._headers

    def append(self, name, value):
        """Add a value to the end of the list for the named header."""
        return self._headers.append(name, value)

    def extend(self, name, values):
        """Extend the list for the named header by appending all values."""
        return self._headers.extend(name, values)

    def insert(self, name, index, value):
        """Insert a value at the passed index in the named header."""
        return self._headers.insert(index, value)

    def remove(self, name, value):
        """
        Remove the first item with the passed value from the
        list for the named header.
        """
        return self._headers.remove(name, value)

    def popvalue(self, name, index=None):
        """Remove the item at the given position in the named header list."""
        return self._headers.popvalue(name, index)

    def index(self, name, value):
        """
        Return the index in the list of the first item whose value is x in
        the values of the named header.
        """
        return self._headers.index(name, value)

    def count(self, name, value):
        """
        Return the number of times a value appears in the list of the values
        of the named header.
        """
        return self._headers.count(name, value)

    def sort(self, name):
        """Sort the items of the list, in place."""
        return self._headers.sort(name)

    def reverse(self, name):
        """Reverse the elements of the list, in place."""
        return self._headers.reverse(name)

    def getlist(self, name):
        """Retrieves the passed header as a sequence of its values."""
        return self._headers.getlist(name)
