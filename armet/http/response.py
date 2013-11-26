# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import collections
import abc
import six
import mimeparse
import weakref
import io
from armet import exceptions
from . import request, client


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
            if self._value != self._headers.get(self._name, ''):
                # If the header value has changed; update our sequence.
                self._value = self._headers.get(self._name, '')
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


class Response(object):
    """Describes the RESTful response abstraction.
    """

    #! Dictionary-like interface to access headers; this should be
    #! set by the dervied class to an instance of a derived Headers class.
    headers = None

    def __init__(self, asynchronous, *args, **kwargs):
        #! True if the response object is closed.
        self._closed = False

        #! True if the response object is streaming.
        self.streaming = False

        #! True if we're asynchronous.
        self.asynchronous = asynchronous

        #! Default the status code to OK.
        self.status = client.OK

        #! A reference to the bound resource; this is set in the resource
        #! view method after traversal.
        self._resource = None

        #! Explicit declaration of character encoding to use when
        #! writing data to the response body.
        #! Defaults to parsing content-type and determining encoding
        #! via the standard rules.
        self._encoding = None

        #! The underlying file stream to write incoming data to.
        self._stream = io.BytesIO()

        #! The content chunk to return to the client.
        self._body = None

        #! The length of the response.
        self._length = 0

    def require_not_closed(self):
        """Raises an exception if the response is closed."""
        if self.closed:
            raise exceptions.InvalidOperation('Response is closed.')

    def require_open(self):
        """Raises an exception if the response is not open."""
        self.require_not_closed()
        if self.streaming:
            raise exceptions.InvalidOperation('Response is streaming.')

    @property
    def status(self):
        """Gets the status code of the response."""
        raise NotImplementedError()

    @status.setter
    def status(self, value):
        """Sets the status code of the response."""
        raise NotImplementedError()

    @property
    def body(self):
        """Returns the current value of the response body."""
        return self._body

    @body.setter
    def body(self, value):
        """Sets the response body to the passed value.

        @note
            During asynchronous or streaming responses, remember that
            the `body` property refers to the portion of the response *not*
            sent to the client.
        """
        self._body = value

    def bind(self, resource):
        """Binds this to the passed resource object.

        @sa armet.http.request.Request.bind
        """
        self._resource = weakref.proxy(resource)

    @property
    def resource(self):
        return self._resource

    @property
    def encoding(self):
        if self._encoding is not None:
            # Encoding has been set manually.
            return self._encoding

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
        self._encoding = value

    @abc.abstractmethod
    def close(self):
        """Flush and close the stream.

        This is called automatically by the base resource on resources
        unless the resource is operating asynchronously; in that case,
        this method MUST be called in order to signal the end of the request.
        If not the request will simply hang as it is waiting for some
        thread to tell it to return to the client.
        """

        # Ensure we're not closed.
        self.require_not_closed()

        if not self.streaming or self.asynchronous:
            # We're not streaming, auto-write content-length if not
            # already set.
            if 'Content-Length' not in self.headers:
                self.headers['Content-Length'] = self.tell()

        # Flush out the current buffer.
        self.flush()

        # We're done with the response; inform the HTTP connector
        # to close the response stream.
        self._closed = True

    @property
    def closed(self):
        """True if the stream is closed."""
        return self._closed

    def tell(self):
        """Return the current stream position."""
        return self._length

    def write(self, chunk, serialize=False, format=None):
        """Writes the given chunk to the output buffer.

        @param[in] chunk
            Either a byte array, a unicode string, or a generator. If `chunk`
            is a generator then calling `self.write(<generator>)` is
            equivalent to:

            @code
                for x in <generator>:
                    self.write(x)
                    self.flush()
            @endcode

        @param[in] serialize
            True to serialize the lines in a determined serializer.

        @param[in] format
            A specific format to serialize in; if provided, no detection is
            done. If not provided, the accept header (as well as the URL
            extension) is looked at to determine an appropriate serializer.
        """

        # Ensure we're not closed.
        self.require_not_closed()

        if chunk is None:
            # There is nothing here.
            return

        if serialize or format is not None:
            # Forward to the serializer to serialize the chunk
            # before it gets written to the response.
            self.serialize(chunk, format=format)
            return  # `serialize` invokes write(...)

        if type(chunk) is six.binary_type:
            # Update the stream length.
            self._length += len(chunk)

            # If passed a byte string, we hope the user encoded it properly.
            self._stream.write(chunk)

        elif isinstance(chunk, six.string_types):
            encoding = self.encoding
            if encoding is not None:
                # If passed a string, we can encode it for the user.
                chunk = chunk.encode(encoding)

            else:
                # Bail; we don't have an encoding.
                raise exceptions.InvalidOperation(
                    'Attempting to write textual data without an encoding.')

            # Update the stream length.
            self._length += len(chunk)

            # Write the encoded data into the byte stream.
            self._stream.write(chunk)

        elif isinstance(chunk, collections.Iterable):
            # If passed some kind of iterator, attempt to recurse into
            # oblivion.
            for section in chunk:
                self.write(section)

        else:
            # Bail; we have no idea what to do with this.
            raise exceptions.InvalidOperation(
                'Attempting to write something not recognized.')

    def serialize(self, data, format=None):
        """Serializes the data into this response using a serializer.

        @param[in] data
            The data to be serialized.

        @param[in] format
            A specific format to serialize in; if provided, no detection is
            done. If not provided, the accept header (as well as the URL
            extension) is looked at to determine an appropriate serializer.

        @returns
            A tuple of the serialized text and an instance of the
            serializer used.
        """
        return self._resource.serialize(data, response=self, format=format)

    def flush(self):
        """Flush the write buffers of the stream.

        This results in writing the current contents of the write buffer to
        the transport layer, initiating the HTTP/1.1 response. This initiates
        a streaming response. If the `Content-Length` header is not given
        then the chunked `Transfer-Encoding` is applied.
        """

        # Ensure we're not closed.
        self.require_not_closed()

        # Pull out the accumulated chunk.
        chunk = self._stream.getvalue()
        self._stream.truncate(0)
        self._stream.seek(0)

        # Append the chunk to the body.
        self.body = chunk if (self._body is None) else (self._body + chunk)

        if self.asynchronous:
            # We are now streaming because we're asynchronous.
            self.streaming = True

    def send(self, *args, **kwargs):
        """Writes the passed chunk and flushes it to the client."""
        self.write(*args, **kwargs)
        self.flush()

    def end(self, *args, **kwargs):
        """
        Writes the passed chunk, flushes it to the client,
        and terminates the connection.
        """
        self.send(*args, **kwargs)
        self.close()

    def __getitem__(self, name):
        """Retrieves a header with the passed name."""
        return self.headers[name]

    def __setitem__(self, name, value):
        """Stores a header with the passed name."""
        self.headers[name] = value

    def __delitem__(self, name):
        """Removes a header with the passed name."""
        del self.headers

    def __len__(self):
        """Retrieves the actual length of the response."""
        return self.tell()

    def __nonzero__(self):
        """Test if the response is closed."""
        return not self._closed

    def __bool__(self):
        """Test if the response is closed."""
        return not self._closed

    def __contains__(self, name):
        """Tests if the passed header exists in the response."""
        return name in self.headers

    def append(self, name, value):
        """Add a value to the end of the list for the named header."""
        return self.headers.append(name, value)

    def extend(self, name, values):
        """Extend the list for the named header by appending all values."""
        return self.headers.extend(name, values)

    def insert(self, name, index, value):
        """Insert a value at the passed index in the named header."""
        return self.headers.insert(index, value)

    def remove(self, name, value):
        """
        Remove the first item with the passed value from the
        list for the named header.
        """
        return self.headers.remove(name, value)

    def popvalue(self, name, index=None):
        """Remove the item at the given position in the named header list."""
        return self.headers.popvalue(name, index)

    def index(self, name, value):
        """
        Return the index in the list of the first item whose value is x in
        the values of the named header.
        """
        return self.headers.index(name, value)

    def count(self, name, value):
        """
        Return the number of times a value appears in the list of the values
        of the named header.
        """
        return self.headers.count(name, value)

    def sort(self, name):
        """Sort the items of the list, in place."""
        return self.headers.sort(name)

    def reverse(self, name):
        """Reverse the elements of the list, in place."""
        return self.headers.reverse(name)

    def getlist(self, name):
        """Retrieves the passed header as a sequence of its values."""
        return self.headers.getlist(name)
