# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
import collections
import abc
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
    def redirect(cls, request, path):
        """Redirect to the canonical URI for this resource.

        @note
            This method does not know how to complete the operation and
            leaves that to an implementation class in a connector. The result
            is the URI to redirect to.
        """
        # Instantiate a new response object.
        response = cls.meta.response()

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

        # Calculate the path to redirect to and set it on the response.
        if cls.meta.trailing_slash:
            path += '/'
        else:
            del path[-1]
        response['Location'] = path

        # Return the response object.
        return response

    @classmethod
    def view(cls, request, path):
        """
        Entry-point of the request cycle; Handles resource creation
        and delegation.

        @param[in] path
            The path accessor for the resource (eg. for a request like
            GET /api/resource/foo/bar/1/4 if resource is mounted on /api/ then
            path will be '/bar/1/4/'

        @param[in] headers
            Dictionary of request headers normalized to have underscores and
            be uppercased.
        """
        try:
            # Parse any arguments out of the path.
            arguments = cls.parse(path)

            # Traverse down the path and determine to resource we're actually
            # accessing.
            resource = cls.traverse(arguments)

            # Instantiate the resource.
            obj = resource(request, **arguments)

            # Initiate the dispatch cycle and return its response.
            response = obj.dispatch()

            # TODO: Commit

            # Return the response from the dispatch cycle.
            return response

        except exceptions.Base as ex:
            # Something that we can handle and return properly happened.
            # TODO: Rollback

            # Instantiate a new response object.
            response = cls.meta.response(status=ex.status)

            # Set the content if we have some.
            # TODO: We need encoders.
            # if ex.content is not None:
            #     response.content = ex.content
            #     response.header('Content-Type', MIMETYPE)

            # Set all headers on the response object.
            for name in ex.headers:
                response[name] = ex.headers[name]

            # Return the response object.
            return response

        except BaseException:
            # Something unexpected happenend.
            # TODO: Rollback

            # Log error message to the logger.
            logger.exception('Internal server error')

            # Return nothing and indicate a server failure.
            # TODO: Pass back the status code (500).
            return None

    #! Precompiled regular expression used to parse out the path.
    _parse_pattern = re.compile(
        r'^(?:\:(?P<query>[^/]+?))?'
        r'(?:\:)?'
        r'(?:/(?P<slug>[^/]+?))?'
        r'(?:/(?P<path>.+?))??'
        r'(?:\.(?P<extension>[^/]+?))??$')

    @classmethod
    def parse(cls, path):
        """Parses out parameters and separates them out of the path."""
        return re.match(cls._parse_pattern, path or '').groupdict()

    @classmethod
    def traverse(cls, arguments):
        """Traverses down the path and determines the accessed resource."""
        # TODO: Implement resource traversal.
        return cls

    def __init__(self, request, **kwargs):
        """Initializes the resources and sets its properites on self.

        @param[in] request
            Request wrapper that communicates accesses to headers and other
            information about the request to the underlying request object
            provided by the HTTP connector.

        @param[in] slug
            The slug that identifies the resource or resources in question.
            If this is being accessed as a list of resources however the slug
            is None.
        """
        self.request = request
        self.__dict__.update(**kwargs)

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

    def make_response(self, content, status=http.client.OK):
        """Constructs a response object from the passed content."""
        # Initialize the response object.
        response = self.meta.response(status=status)

        # TODO: Prepare the data for transmission.
        # TODO: Encode the data using a desired encoder.
        # TODO: Generate appropriate headers.

        # Return the built response.
        return response

    def dispatch(self):
        """Entry-point of the dispatch cycle for this resource.

        Performs common work such as authentication, decoding, etc. before
        handing complete control of the result to a function with the
        same name as the request method.
        """
        # TODO: Assert authentication and attempt to get a valid user object.

        # TODO: Assert accessibiltiy of the resource in question.
        # if not self.authorization.is_accessible(self.user):
        #     # If a resource is not accessible then we return 404 as the
        #     #   resource in its entirety is hidden from this user.
        #     raise exceptions.NotFound()

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
        """Processes a `GET` request.

        @returns
            The response to return to the client.
        """
        # Ensure we're allowed to read the resource.
        self.assert_operations('read')

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.slug is not None:
            if not items:
                # Requested a specific resource but nothing is returned.
                raise exceptions.NotFound()

            if not isinstance(items, six.string_types):
                if isinstance(items, collections.Sequence):
                    try:
                        # Ensure that we only return a single object
                        # if we're requested to.
                        items = items[0]

                    except TypeError:
                        # Assume that `items` is already a single object.
                        pass

        # Build and return the response object
        return self.make_response(items)

    @abc.abstractmethod
    def read(self):
        """Retrieves data to be displayed; called via GET.

        @returns
            Either a single object or an iterable of objects to be encoded
            and returned to the client.
        """
        # There is no default behavior.

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
