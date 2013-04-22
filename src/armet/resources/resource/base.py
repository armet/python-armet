# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import six
import collections
import mimeparse
from armet import http, utils


logger = logging.getLogger(__name__)


class Resource(object):
    """Implements the RESTful resource protocol for abstract resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    @classmethod
    def redirect(cls, request, response):
        """Redirect to the canonical URI for this resource."""
        if cls.meta.legacy_redirect:
            if request.method in ('GET', 'HEAD',):
                # A SAFE request is allowed to redirect using a 301
                response.status = http.client.MOVED_PERMANENTLY

            else:
                # All other requests must use a 307
                response.status = http.client.TEMPORARY_REDIRECT

        else:
            # Modern redirects are allowed. Let's have some fun.
            # Hopefully you're client supports this.
            # The RFC explicitly discourages UserAgent sniffing.
            response.status = http.client.PERMANENT_REDIRECT

        # Terminate the connection.
        response.close()

    @classmethod
    def view(cls, request, response):
        """
        Entry-point of the request / response cycle; Handles resource creation
        and delegation.

        @param[in] requset
            The HTTP request object; containing accessors for information
            about the request.

        @param[in] response
            The HTTP response object; contains accessors for modifying
            the information that will be sent to the client.
        """
        # Determine if we need to redirect.
        test = cls.meta.trailing_slash
        uri = request.uri
        if test ^ uri.endswith('/'):
            # Massage the URL by removing or adding the trailing slash.
            response['Location'] = uri + '/' if test else uri[:-1]

            # Redirect to the version with the correct trailing slash.
            return cls.redirect(request, response)

        try:
            # Instantiate the resource.
            obj = cls(request, response)

            # Initiate the dispatch cycle.
            result = obj.dispatch()
            if not response.asynchronous:
                # There is several things that dispatch is allowed to return.
                if result is None:
                    # If there was no result from dispatch; just
                    # close the response.
                    response.close()

                elif isinstance(result, six.string_types):
                    # If `chunk` is some kind of string; just write it out
                    # and close the response.
                    response.write(result)
                    response.close()

                elif isinstance(result, collections.Iterable):
                    # This should be some kind of iterable, perhaps
                    # a generator.
                    def stream():
                        # Iterate and yield the chunks to the network
                        # stream.
                        for chunk in result:
                            # Write the chunk.
                            response.write(chunk)
                            response.flush()

                            # Yield control to the connector to further
                            # do whatever it needs to do.
                            yield

                        # Close the response.
                        response.close()

                    # Return our streaming method.
                    return stream()

                else:
                    # We've got something here; naively coerce this to
                    # a binary string.
                    response.write(six.binary_type(result))
                    response.close()

        except http.exceptions.BaseHTTPException as e:
            # Something that we can handle and return properly happened.
            # Set response propertie    s from the exception.
            response.status = e.status
            response.headers.update(e.headers)

            if e.content:
                # Write the exception body if present and close
                # the response.
                # TODO: Use the plain-text encoder.
                cls.serialize(e.content, response, format='json')

            # Terminate the connection.
            response.close()

        except BaseException as e:
            # Something unexpected happenend.
            # Log error message to the logger.
            logger.exception('Internal server error')

            # TODO: Don't do the following if not in DEBUG mode.
            raise

    def __init__(self, request, response):
        """Initialize; store the given request and response objects."""
        self.request = request
        self.response = response

    @utils.boundmethod
    def serialize(obj, data, response=None, request=None, format=None):
        """Serializes the data using a serializer.

        @param[in] data
            The data to be serialized.

        @param[in] response
            The response object to serialize the data to.
            If this method is invoked as an instance method, the response
            object can be omitted and it will be taken from the instance.

        @param[in] request
            The request object to pull information from; normally used to
            determine the encoding format (when `format` is not provided).
            May be used by some serializers as well to pull additional headers.
            If this method is invoked as an instance method, the request
            object can be omitted and it will be taken from the instance.

        @param[in] format
            A specific format to serialize in; if provided, no detection is
            done. If not provided, the accept header (as well as the URL
            extension) is looked at to determine an appropriate serializer.

        @returns
            The instance of the used serializer, if any.
        """
        if isinstance(obj, Resource):
            if not request:
                # Ensure we have a request object.
                request = obj.request

            if not response:
                # Ensure we have a response object.
                response = obj.response

        Serializer = None
        if format:
            # An explicit format was given; do not attempt to auto-detect
            # a serializer.
            Serializer = obj.meta.serializers[format]

        if not Serializer:
            # Determine an appropriate serializer to use by
            # introspecting the request object and looking at the `Accept`
            # header.
            media_ranges = request.get('Accept', '*/*').strip()
            if not media_ranges:
                # Default the media ranges to */*
                media_ranges = '*/*'

            if media_ranges != '*/*':
                # Parse the media ranges and determine the serializer
                # that is the closest match.
                media_types = six.iterkeys(obj._serializer_map)
                media_type = mimeparse.best_match(media_types, media_ranges)
                if media_type:
                    format = obj._serializer_map[media_type]
                    Serializer = obj.meta.serializers[format]

            else:
                # Client indicated no preference; use the default.
                Serializer = obj.meta.serializers[obj.meta.default_serializer]

        if Serializer:
            try:
                # Attempt to serialize the data using the determined
                # serializer.
                serializer = Serializer(request, response)
                serializer.serialize(data)

                # Return the instance of the serializer used.
                return serializer

            except ValueError:
                # Failed to serialize the data.
                pass

        # Either failed to determine a serializer or failed to serialize
        # the data; construct a list of available and valid encoders.
        available = {}
        for name in obj.meta.allowed_serializers:
            Serializer = obj.meta.serializers[name]
            instance = Serializer(request, None)
            if instance.can_serialize(data):
                available[name] = Serializer.media_types[0]

        # Raise a Not Acceptable exception.
        raise http.exceptions.NotAcceptable(available)

    def assert_http_allowed_methods(self):
        """Ensure that we're allowed to use this HTTP method."""
        if self.request.method not in self.meta.http_allowed_methods:
            # The specified method is not allowed for the resource
            # identified by the request URI.
            # RFC 2616 § 10.4.6 — 405 Method Not Allowed
            raise http.exceptions.MethodNotAllowed(
                self.meta.http_allowed_methods)

    def dispatch(self):
        """Entry-point of the dispatch cycle for this resource.

        Performs common work such as authentication, decoding, etc. before
        handing complete control of the result to a function with the
        same name as the request method.
        """
        # TODO: Assert authentication and attempt to get a valid user object.
        # TODO: Assert accessibiltiy of the resource in question.

        # Ensure that we understand the HTTP method.
        if self.request.method not in self.meta.http_method_names:
            # This is the appropriate response when the server does
            # not recognize the request method.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise http.exceptions.NotImplemented()

        # Ensure that we're allowed to use this HTTP method.
        self.assert_http_allowed_methods()

        # Retrieve the function corresponding to this HTTP method.
        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Server is not capable of supporting it.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise http.exceptions.NotImplemented()

        # Delegate to the determined function to process the request.
        return function()
