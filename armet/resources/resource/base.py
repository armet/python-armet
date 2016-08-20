# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
import re
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

    #! Instantiated options class; contains all merged properties
    #! from the class hierarchy's Meta classes.
    meta = None

    #! Maps media ranges to deserializer names.
    #! Generated by the metaclass.
    _deserializer_map = None

    #! Maps media ranges to serializer names.
    #! Generated by the metaclass.
    _serializer_map = None

    def __new__(cls, request, response, *args, **kwargs):
        # Parse any arguments out of the path and traverse down the
        # path using any defined patterns.
        cls, params = cls.traverse(request)

        # Actually construct the resource and return the instance.
        obj = super(Resource, cls).__new__(cls)

        # Update our instance dictionary with the arugments from `parse`.
        obj.__dict__.update(params)

        # Return our constructed instance.
        return obj

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
            # Instantiate the resource.
            obj = cls(request, response)

            # Bind the request and response objects to the constructed
            # resource.
            request.bind(obj)
            response.bind(obj)

            # Bind the request object to the resource.
            # This is used to facilitate the serializer and deserializer.
            obj._request = request

            # Initiate the dispatch cycle and handle its result on
            # synchronous requests.
            result = obj.dispatch(request, response)

            if not response.asynchronous:
                # There is several things that dispatch is allowed to return.
                if (isinstance(result, collections.Iterable) and
                        not isinstance(result, six.string_types)):
                    # Return the stream generator.
                    return cls.stream(response, result)

                else:
                    # Leave it up to the response to throw or write whatever
                    # we got back.
                    response.end(result)
                    if response.body:
                        # Return the body if there was any set.
                        return response.body

        except http.exceptions.BaseHTTPException as e:
            # Something that we can handle and return properly happened.
            # Set response properties from the exception.
            response.status = e.status
            response.headers.update(e.headers)

            if e.content:
                # Write the exception body if present and close
                # the response.
                # TODO: Use the plain-text encoder.
                response.send(e.content, serialize=True, format='json')

            # Terminate the connection and return the body.
            response.close()
            if response.body:
                return response.body

        except Exception:
            # Something unexpected happened.
            # Log error message to the logger.
            logger.exception('Internal server error')

            # Write a debug message for the client.
            if not response.streaming and not response.closed:
                response.status = http.client.INTERNAL_SERVER_ERROR
                response.headers.clear()
                response.close()

    @classmethod
    def parse(cls, path):
        """Parses out parameters and separates them out of the path.

        This uses one of the many defined patterns on the options class. But,
        it defaults to a no-op if there are no defined patterns.
        """
        # Iterate through the available patterns.
        for resource, pattern in cls.meta.patterns:
            # Attempt to match the path.
            match = re.match(pattern, path)
            if match is not None:
                # Found something.
                return resource, match.groupdict(), match.string[match.end():]

        # No patterns at all; return unsuccessful.
        return None if not cls.meta.patterns else False

    @classmethod
    def traverse(cls, request, params=None):
        """Traverses down the path and determines the accessed resource.

        This makes use of the patterns array to implement simple traversal.
        This defaults to a no-op if there are no defined patterns.
        """
        # Attempt to parse the path using a pattern.
        result = cls.parse(request.path)
        if result is None:
            # No parsing was requested; no-op.
            return cls, {}

        elif not result:
            # Parsing failed; raise 404.
            raise http.exceptions.NotFound()

        # Partition out the result.
        resource, data, rest = result

        if params:
            # Append params to data.
            data.update(params)

        if resource is None:
            # No traversal; return parameters.
            return cls, data

        # Modify the path appropriately.
        if data.get('path') is not None:
            request.path = data.pop('path')

        elif rest is not None:
            request.path = rest

        # Send us through traversal again.
        result = resource.traverse(request, params=data)
        return result

    @classmethod
    def stream(cls, response, sequence):
        """
        Helper method used in conjunction with the view handler to
        stream responses to the client.
        """
        # Construct the iterator and run the sequence once in order
        # to capture any headers and status codes set.
        iterator = iter(sequence)
        data = {'chunk': next(iterator)}
        response.streaming = True

        def streamer():
            # Iterate through the iterator and yield its content
            while True:
                if response.asynchronous:
                    # Yield our current chunk.
                    yield data['chunk']

                else:
                    # Write the chunk to the response
                    response.send(data['chunk'])

                    # Yield its body
                    yield response.body

                    # Unset the body.
                    response.body = None

                try:
                    # Get the next chunk.
                    data['chunk'] = next(iterator)

                except StopIteration:
                    # Get out of the loop.
                    break

            if not response.asynchronous:
                # Close the response.
                response.close()

        # Return the streaming function.
        return streamer()

    @utils.boundmethod
    def deserialize(self, request=None, text=None, format=None):
        """Deserializes the text using a determined deserializer.

        @param[in] request
            The request object to pull information from; normally used to
            determine the deserialization format (when `format` is
            not provided).

        @param[in] text
            The text to be deserialized. Can be left blank and the
            request will be read.

        @param[in] format
            A specific format to deserialize in; if provided, no detection is
            done. If not provided, the content-type header is looked at to
            determine an appropriate deserializer.

        @returns
            A tuple of the deserialized data and an instance of the
            deserializer used.
        """
        if isinstance(self, Resource):
            if not request:
                # Ensure we have a response object.
                request = self._request

        Deserializer = None
        if format:
            # An explicit format was given; do not attempt to auto-detect
            # a deserializer.
            Deserializer = self.meta.deserializers[format]

        if not Deserializer:
            # Determine an appropriate deserializer to use by
            # introspecting the request object and looking at
            # the `Content-Type` header.
            media_ranges = request.get('Content-Type')
            if media_ranges:
                # Parse the media ranges and determine the deserializer
                # that is the closest match.
                media_types = six.iterkeys(self._deserializer_map)
                media_type = mimeparse.best_match(media_types, media_ranges)
                if media_type:
                    format = self._deserializer_map[media_type]
                    Deserializer = self.meta.deserializers[format]

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
                data = deserializer.deserialize(request=request, text=text)
                return data, deserializer

            except ValueError:
                # Failed to deserialize the data.
                pass

        # Failed to determine a deserializer; or failed to deserialize.
        raise http.exceptions.UnsupportedMediaType()

    @utils.boundmethod
    def serialize(self, data, response=None, request=None, format=None):
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
        if isinstance(self, Resource):
            if not request:
                # Ensure we have a response object.
                request = self._request

        Serializer = None
        if format:
            # An explicit format was given; do not attempt to auto-detect
            # a serializer.
            Serializer = self.meta.serializers[format]

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
                media_types = six.iterkeys(self._serializer_map)
                media_type = mimeparse.best_match(media_types, media_ranges)
                if media_type:
                    format = self._serializer_map[media_type]
                    Serializer = self.meta.serializers[format]

            else:
                # Client indicated no preference; use the default.
                default = self.meta.default_serializer
                Serializer = self.meta.serializers[default]

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
        for name in self.meta.allowed_serializers:
            Serializer = self.meta.serializers[name]
            instance = Serializer(request, None)
            if instance.can_serialize(data):
                available[name] = Serializer.media_types[0]

        # Raise a Not Acceptable exception.
        raise http.exceptions.NotAcceptable(available)

    @classmethod
    def _process_cross_domain_request(cls, request, response):
        """Facilitate Cross-Origin Requests (CORs).
        """

        # Step 1
        # Check for Origin header.
        origin = request.get('Origin')
        if not origin:
            return

        # Step 2
        # Check if the origin is in the list of allowed origins.
        if not (origin in cls.meta.http_allowed_origins or
                '*' == cls.meta.http_allowed_origins):
            return

        # Step 3
        # Try to parse the Request-Method header if it exists.
        method = request.get('Access-Control-Request-Method')
        if method and method not in cls.meta.http_allowed_methods:
            return

        # Step 4
        # Try to parse the Request-Header header if it exists.
        headers = request.get('Access-Control-Request-Headers', ())
        if headers:
            headers = [h.strip() for h in headers.split(',')]

        # Step 5
        # Check if the headers are allowed on this resource.
        allowed_headers = [h.lower() for h in cls.meta.http_allowed_headers]
        if any(h.lower() not in allowed_headers for h in headers):
            return

        # Step 6
        # Always add the origin.
        response['Access-Control-Allow-Origin'] = origin

        # TODO: Check if we can provide credentials.
        response['Access-Control-Allow-Credentials'] = 'true'

        # Step 7
        # TODO: Optionally add Max-Age header.

        # Step 8
        # Add the allowed methods.
        allowed_methods = ', '.join(cls.meta.http_allowed_methods)
        response['Access-Control-Allow-Methods'] = allowed_methods

        # Step 9
        # Add any allowed headers.
        allowed_headers = ', '.join(cls.meta.http_allowed_headers)
        if allowed_headers:
            response['Access-Control-Allow-Headers'] = allowed_headers

        # Step 10
        # Add any exposed headers.
        exposed_headers = ', '.join(cls.meta.http_exposed_headers)
        if exposed_headers:
            response['Access-Control-Expose-Headers'] = exposed_headers

    def __init__(self, request, response):
        # Store the request and response objects on self.
        self.request = request
        self.response = response

    def dispatch(self, request, response):
        """Entry-point of the dispatch cycle for this resource.

        Performs common work such as authentication, decoding, etc. before
        handing complete control of the result to a function with the
        same name as the request method.
        """
        # Assert authentication and attempt to get a valid user object.
        self.require_authentication(request)

        # Assert accessibiltiy of the resource in question.
        self.require_accessibility(request.user, request.method)

        # Facilitate CORS by applying various headers.
        # This must be done on every request.
        # TODO: Provide cross_domain configuration that turns this off.
        self._process_cross_domain_request(request, response)

        # Route the HTTP/1.1 request to an appropriate method.
        return self.route(request, response)

    def require_authentication(self, request):
        """Ensure we are authenticated."""
        request.user = user = None

        if request.method == 'OPTIONS':
            # Authentication should not be checked on an OPTIONS request.
            return

        for auth in self.meta.authentication:
            user = auth.authenticate(request)
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
            request.user = user
            return

        if not user and not auth.allow_anonymous:
            # No authenticated user found and protocol doesn't allow
            # anonymous users.
            auth.unauthenticated()

    def require_accessibility(self, user, method):
        """Ensure we are allowed to access this resource."""
        if method == 'OPTIONS':
            # Authorization should not be checked on an OPTIONS request.
            return

        authz = self.meta.authorization
        if not authz.is_accessible(user, method, self):
            # User is not authorized; raise an appropriate message.
            authz.unaccessible()

    def require_http_allowed_method(cls, request):
        """Ensure that we're allowed to use this HTTP method."""
        allowed = cls.meta.http_allowed_methods
        if request.method not in allowed:
            # The specified method is not allowed for the resource
            # identified by the request URI.
            # RFC 2616 § 10.4.6 — 405 Method Not Allowed
            raise http.exceptions.MethodNotAllowed(allowed)

    def route(self, request, response):
        """Processes every request.

        Directs control flow to the appropriate HTTP/1.1 method.
        """
        # Ensure that we're allowed to use this HTTP method.
        self.require_http_allowed_method(request)

        # Retrieve the function corresponding to this HTTP method.
        function = getattr(self, request.method.lower(), None)
        if function is None:
            # Server is not capable of supporting it.
            raise http.exceptions.NotImplemented()

        # Delegate to the determined function to process the request.
        return function(request, response)

    def options(self, request, response):
        """Process an `OPTIONS` request.

        Used to initiate a cross-origin request. All handling specific to
        CORS requests is done on every request however this method also
        returns a list of available methods.
        """
        # Gather a list available HTTP/1.1 methods for this URI.
        response['Allowed'] = ', '.join(self.meta.http_allowed_methods)

        # All CORS handling is done for every HTTP/1.1 method.
        # No more handling is neccesary; set the response to 200 and return.
        response.status = http.client.OK