# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
import collections
import re
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
            # Parse any arguments out of the path.
            arguments = cls.parse(request.path)

            # Traverse down the path and determine to resource we're actually
            # accessing.
            Resource = cls.traverse(arguments)

            # Instantiate the resource.
            obj = Resource(request, response, **arguments)

            # Initiate the dispatch cycle.
            obj.dispatch()

            # TODO: Commit

        except exceptions.Base as e:
            # Something that we can handle and return properly happened.

            # TODO: Rollback

            # Set response properties from the exception.
            response.status = e.status
            for name in e.headers:
                response[name] = e.headers[name]

            if e.content:
                # Write the exception body if present.
                response.write(e.content)

        except BaseException as e:
            # Something unexpected happenend.

            # TODO: Rollback

            # Log error message to the logger.
            logger.exception('Internal server error')

            # TODO: Don't do the following if not in DEBUG mode.
            raise

    #! Precompiled regular expression used to parse out the path.
    _parse_pattern = re.compile(
        r'^'
        r'(?:\:(?P<directives>[^/\(\)]*))?'
        r'(?:\((?P<query>[^/]*)\))?'
        r'(?:/(?P<slug>[^/]+?))?'
        r'(?:/(?P<path>.+?))??'
        r'(?:\.(?P<extensions>[^/]+?))??/??$')

    @classmethod
    def parse(cls, path=''):
        """Parses out parameters and separates them out of the path."""
        # Apply the compiled regex.
        arguments = re.match(cls._parse_pattern, path).groupdict()

        # Explode the list arguments; they should be represented as
        # empty arrays and not None.
        if arguments['extensions']:
            arguments['extensions'] = arguments['extensions'].split('.')

        else:
            arguments['extensions'] = []

        if arguments['directives']:
            arguments['directives'] = arguments['directives'].split(':')

        else:
            arguments['directives'] = []

        # Return the arguments
        return arguments

    @classmethod
    def traverse(cls, arguments):
        """Traverses down the path and determines the accessed resource."""
        # TODO: Implement resource traversal.
        return cls

    def __init__(self, request, response, **kwargs):
        """Initializes the resources and sets its properites on self."""
        # Store the given request and response objects.
        self.request = request
        self.response = response

        # Update our instance dictionary with the arugments from `parse`.
        # Note that this adds the 'directives', 'query', 'slug', 'path', and
        # 'extensions' attributes.
        self.__dict__.update(**kwargs)

        if self.slug:
            # Clean the incoming slug value from the URI, if any.
            self.slug = self.meta.slug.clean(self.slug)
            self.slug = self.slug_clean(self.slug)

    @property
    def http_allowed_methods(self):
        """Retrieves the allowed HTTP methods for this request."""
        if self.slug is not None:
            return self.meta.http_detail_allowed_methods

        return self.meta.http_list_allowed_methods

    @property
    def allowed_operations(self):
        """Retrieves the allowed operations for this request."""
        if self.slug is not None:
            return self.meta.detail_allowed_operations

        return self.meta.list_allowed_operations

    def assert_operations(self, *args):
        """Assets if the requested operations are allowed in this context."""
        operations = self.allowed_operations
        for operation in args:
            if operation not in operations:
                raise exceptions.Forbidden()

    def make_response(self, data, status=http.client.OK):
        """Fills the response object from the passed data."""
        # Prepare the data for transmission.
        data = self.prepare(data)

        # Encode the data using a desired encoder.
        self.encode(data)

        # Make sure that the status code is set.
        self.response.status = status

    def prepare(self, data):
        """Prepares the data for encoding."""
        if data is None:
            # No data; return nothing.
            return None

        if self.slug is None:
            # Attempt to prepare each item of the iterable (as long as
            # we're not a string or some sort of mapping).
            return (self.item_prepare(x) for x in data)

        # Prepare just the singular value and return.
        return self.item_prepare(data)

    def item_prepare(self, item):
        """Prepares a single item for encoding."""
        # Initialize the object that hold the resultant item.
        obj = {}

        # Iterate through the attributes and build the object
        # from the item.
        for name, attribute in six.iteritems(self.attributes):
            if not attribute.include:
                # Attribute is not to be included in the
                # resource body.
                continue

            try:
                # Apply the attribute; request the value of the
                # attribute from the item.
                value = attribute.get(item)

            except (TypeError, ValueError, KeyError, AttributeError):
                # Nothing found; set it to null.
                value = None

            # Run the attribute through the prepare cycle.
            value = attribute.prepare(value)
            value = self.preparers[name](self, item, value)

            # Set the value on the object.
            obj[name] = value

        # Return the resultant object.
        return obj

    def slug_prepare(self, obj, value):
        """Prepares the slug for constructing a URI."""
        return value

    def slug_clean(self, value):
        """Cleans the incoming slug into an expected represention."""
        return value

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
        if self.request.method not in self.http_allowed_methods:
            # The specified method is not allowed for the resource
            # identified by the request URI.
            # RFC 2616 § 10.4.6 — 405 Method Not Allowed
            raise exceptions.MethodNotAllowed(self.http_allowed_methods)

        # Retrieve the function corresponding to this HTTP method.
        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Server is not capable of supporting it.
            # RFC 2616 § 10.5.2 — 501 Not Implemented
            raise exceptions.NotImplemented()

        # Delegate to the determined function to process the request.
        return function()

    def get(self):
        """Processes a `GET` request."""
        # Ensure we're allowed to read the resource.
        self.assert_operations('read')

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.slug is not None:
            if not items:
                # Requested a specific resource but nothing is returned.
                raise exceptions.NotFound()

            if (not isinstance(items, six.string_types) and
                    isinstance(items, collections.Sequence)):
                try:
                    # Ensure that we only return a single object
                    # if we're requested to.
                    items = items[0]

                except (TypeError, AttributeError):
                    # Assume that `items` is already a single object.
                    pass

        # Build the response object.
        self.make_response(items)

    def read(self):
        """Retrieves data to be displayed; called via GET.

        @returns
            Either a single object or an iterable of objects to be encoded
            and returned to the client.
        """
        # There is no default behavior.
        raise exceptions.NotImplemented()

    def create(self, data):
        """Creates the object that is being requested; via POST or PUT.

        @param[in] data
            The data to create the object with.

        @returns
            The object that has been created; or, None, to indicate that no
            object was created.
        """
        # There is no default behavior.
        raise exceptions.NotImplemented()

    def update(self, obj, data):
        """Updates the object that is being requested; via PATCH or PUT.

        @param[in] obj
            The objects represented by the current request; the results of
            invoking `self.read()`.

        @param[in] data
            The data to update the object with.

        @returns
            The object that has been updated.
        """
        # There is no default behavior.
        raise exceptions.NotImplemented()

    def destroy(self, obj):
        """Destroy the passed object (or objects).

        @param[in] obj
            The objects represented by the current request; the results of
            invoking `self.read()`.

        @returns
            Nothing.
        """
        # There is no default behavior.
        raise exceptions.NotImplemented()
