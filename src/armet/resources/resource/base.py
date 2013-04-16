# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging
from armet import http
from armet.http import exceptions


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
        url = request.url
        if test ^ url.endswith('/'):
            # Massage the URL by removing or adding the trailing slash.
            response['Location'] = url + '/' if test else url[:-1]

            # Redirect to the version with the correct trailing slash.
            return cls.redirect(request, response)

        try:
            # Instantiate the resource.
            obj = cls(request, response)

            # Initiate the dispatch cycle.
            obj.dispatch()

        except exceptions.Base as e:
            # Something that we can handle and return properly happened.

            # Set response properties from the exception.
            response.status = e.status
            for name in e.headers:
                response[name] = e.headers[name]

            if e.content:
                # Write the exception body if present.
                response.write(e.content)

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

    def encode(self, data):
        """Encodes the data using a selected encoder."""
        # Determine the appropriate encoder to use by reading
        # the request object.
        accept = self.request.get('Accept')
        encoder = None
        if not accept:
            # Default the accept header to */*
            accept = '*/*'

        allowed = self.meta.allowed_encoders
        if self.extensions and self.extensions[-1] in allowed:
            name = self.extensions[-1].lower()
            if name in allowed:
                match = self.meta.encoders[name]
            if match is not None and match.can_transcode(accept):
                # An encoder of the same name was discovered and
                # it matches the requested format.
                encoder = match

        elif accept.strip() != '*/*':
            # No specific format specified in the URL; iterate through
            # encoders until one matches the specification defined
            # in the Accept header.
            for name in allowed:
                match = self.meta.encoders[name]
                if match.can_transcode(accept):
                    # An encoder has matched to the format.
                    encoder = match
                    break

        else:
            # Resort to the default encoder.
            encoder = self.meta.encoders[self.meta.default_encoder]

        if encoder:
            try:
                # Attempt to encode the data using the determined encoder.
                instance = encoder(accept, self.request, self.response)
                return instance.encode(data)

            except ValueError:
                # Failed to encode the data.
                pass

        # Either failed to determine an encoder or failed to encode
        # the data; construct a list of available and valid encoders.
        available = {}
        for name in self.meta.allowed_encoders:
            encoder = self.meta.encoders[name]
            instance = encoder(accept, self.request, self.response)
            if instance.can_encode(data):
                available[name] = encoder.mimetype

        # Raise a Not Acceptable exception.
        raise exceptions.NotAcceptable(available)

    def assert_http_allowed_methods(self):
        """Ensure that we're allowed to use this HTTP method."""
        if self.request.method not in self.meta.http_allowed_methods:
            # The specified method is not allowed for the resource
            # identified by the request URI.
            # RFC 2616 § 10.4.6 — 405 Method Not Allowed
            raise exceptions.MethodNotAllowed(self.meta.http_allowed_methods)

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
            raise exceptions.NotImplemented()

        # Ensure that we're allowed to use this HTTP method.
        self.assert_http_allowed_methods()

        # Retrieve the function corresponding to this HTTP method.
        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Server is not capable of supporting it.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise exceptions.NotImplemented()

        # Delegate to the determined function to process the request.
        return function()
