# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import six
import collections
import mimeparse
import traceback
from armet import http, utils, authentication


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
        if test ^ request.path.endswith('/'):
            # Construct a new URL by removing or adding the trailing slash.
            path = request.path + '/' if test else request.path[:-1]
            response['Location'] = '{}://{}{}{}{}'.format(
                request.protocol.lower(),
                request.host,
                request.mount_point,
                path,
                '?' + request.query if request.query else '')

            # Redirect to the version with the correct trailing slash.
            return cls.redirect(request, response)

        try:
            # arguments = cls.parse(request.path)
            # cls = cls.traverse(arguments)

            # Bind the request and response to the resource class object.
            request._Resource = response._Resource = cls

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
                            if chunk:
                                # Write the chunk and flush.
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

        except Exception:
            # Something unexpected happened.

            # Log error message to the logger.
            logger.exception('Internal server error')

            # Write a debug message for the client.
            if not response.streaming and not response.closed:
                response.clear()
                response.status = http.client.INTERNAL_SERVER_ERROR
                if cls.meta.debug:
                    # We're debugging; write the traceback.
                    response['Content-Type'] = 'text/plain'
                    response.write(traceback.format_exc())

                response.close()

    def __init__(self, request, response):
        """Initialize; store the given request and response objects."""
        self.request = request
        self.response = response

    @utils.boundmethod
    def deserialize(obj, text, request=None, format=None):
        """Deserializes the text using a determined deserializer.

        @param[in] text
            The text to be deserialized.

        @param[in] request
            The request object to pull information from; normally used to
            determine the deserialization format (when `format` is
            not provided).

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @returns
            A tuple of the deserialized data and an instance of the
            deserializer used.
        """
        if isinstance(obj, Resource):
            if not request:
                # Ensure we have a response object.
                request = obj.request

        Deserializer = None
        if format:
            # An explicit format was given; do not attempt to auto-detect
            # a deserializer.
            Deserializer = obj.meta.deserializers[format]

        if not Deserializer:
            # Determine an appropriate deserializer to use by
            # introspecting the request object and looking at
            # the `Content-Type` header.
            media_ranges = request.get('Content-Type')
            if media_ranges:
                # Parse the media ranges and determine the deserializer
                # that is the closest match.
                media_types = six.iterkeys(obj._deserializer_map)
                media_type = mimeparse.best_match(media_types, media_ranges)
                if media_type:
                    format = obj._deserializer_map[media_type]
                    Deserializer = obj.meta.deserializers[format]

            else:
                # Client didn't provide a content-type; we're supposed
                # to auto-detect.
                # TODO: Implement this.
                pass

        if Deserializer:
            try:
                # Attempt to deserialize the data using the determined
                # deserializer.
                deserializer = Deserializer()
                return deserializer.deserialize(text), deserializer

            except ValueError:
                # Failed to deserialize the data.
                pass

        # Failed to determine a deserializer; or failed to deserialize.
        raise http.exceptions.UnsupportedMediaType()

    @utils.boundmethod
    def serialize(obj, data, response=None, request=None, format=None):
        """Serializes the data using a determined serializer.

        @param[in] data
            The data to be serialized.

        @param[in] response
            The response object to serialize the data to.
            If this method is invoked as an instance method, the response
            object can be omitted and it will be taken from the instance.

        @param[in] request
            The request object to pull information from; normally used to
            determine the serialization format (when `format` is not provided).
            May be used by some serializers as well to pull additional headers.
            If this method is invoked as an instance method, the request
            object can be omitted and it will be taken from the instance.

        @param[in] format
            A specific format to serialize in; if provided, no detection is
            done. If not provided, the accept header (as well as the URL
            extension) is looked at to determine an appropriate serializer.

        @returns
            A tuple of the serialized text and an instance of the
            serializer used.
        """
        if isinstance(obj, Resource):
            if not request:
                # Ensure we have a request object.
                request = obj.request

        Serializer = None
        if format:
            # An explicit format was given; do not attempt to auto-detect
            # a serializer.
            Serializer = obj.meta.serializers[format]

        if not Serializer:
            # Determine an appropriate serializer to use by
            # introspecting the request object and looking at the `Accept`
            # header.
            media_ranges = (request.get('Accept') or '*/*').strip()
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
                return serializer.serialize(data), serializer

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
        # Assert authentication and attempt to get a valid user object.
        self.user = user = None
        for auth in self.meta.authentication:
            user = auth.authenticate(self)
            if user is False:
                # Authentication protocol failed to authenticate;
                # pass the baton.
                continue

            if user is None and not auth.allow_anonymous:
                # Authentication protocol determined the user is
                # unauthenticated.
                auth.unauthenticated()

            # Authentication protocol determined the user is indeed
            # authenticated (or not); Store the user for later reference.
            self.user = user
            break

        if not user and not auth.allow_anonymous:
            # No authenticated user found and protocol doesn't allow
            # anonymous users.
            auth.unauthenticated()

        # TODO: Assert accessibiltiy of the resource in question.

        # Ensure that we understand the HTTP method.
        if self.request.method not in self.meta.http_method_names:
            # This is the appropriate response when the server does
            # not recognize the request method.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise http.exceptions.NotImplemented()

        # Ensure that we're allowed to use this HTTP method.
        self.assert_http_allowed_methods()

        # Delegate to the determined function to process the request.
        return self.route()()

    def route(self):
        """Route the HTTP method to the handling function."""
        # Retrieve the function corresponding to this HTTP method.
        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Server is not capable of supporting it.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise http.exceptions.NotImplemented()

        # Delegate to the determined function to process the request.
        return function

    def options(self):
        """Process an `OPTIONS` request.

        Used to initiate in cross origin requests.
        """
        # Set the initial response code to 200.
        self.response.status = http.client.OK

        # Step 1
        # Check for Origin header.
        origin = self.request.get('Origin')
        if not origin:
            return

        # Step 2
        # Check if the origin is in the list of allowed origins.
        if not (origin in self.meta.http_allowed_origins or
                '*' == self.meta.http_allowed_origins):
            return

        # Step 3
        # Try to parse the Request-Method header if it exists.
        method = self.request.get('Access-Control-Request-Method')
        if not method or method not in self.meta.http_method_names:
            return

        # Step 4
        # Try to parse the Request-Header header if it exists.
        headers = self.request.get('Access-Control-Request-Headers', ())
        if headers:
            headers = headers.split(',')

        # Step 5
        # Check if the method is allowed on this resource.
        if method not in self.meta.http_allowed_methods:
            return

        # Step 6
        # Check if the headers are allowed on this resource.
        allowed_headers = (h.lower() for h in self.meta.http_allowed_headers)
        if any(h.lower() not in allowed_headers for h in headers):
            return

        # Step 7
        # Always add the origin.
        self.response['Access-Control-Allow-Origin'] = origin

        # Check if we can provide credentials.
        authn = self.meta.authentication
        if (authn and type(authn[0]) is not authentication.Authentication):
            response['Access-Control-Allow-Credentials'] = 'true'

        # Step 8
        # TODO: Optionally add Max-Age header.

        # Step 9
        # Add the allowed methods.
        allowed_methods = ','.join(self.meta.http_allowed_methods)
        response['Access-Control-Allow-Methods'] = allowed_methods

        # Step 10
        # Add any allowed headers.
        allowed_headers = ','.join(self.meta.http_allowed_headers)
        if allowed_headers:
            response['Access-Control-Allow-Headers'] = allowed_headers
