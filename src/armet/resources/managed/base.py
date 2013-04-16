# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import logging
from ..resource import base
import re
import six
from armet import http


logger = logging.getLogger(__name__)


class ManagedResource(base.Resource):
    """Implements the RESTful resource protocol for managed resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.ManagedResource` (defined in
        the `__init__.py`).
    """

    def __new__(cls, request, response):
        # Parse any arguments out of the path.
        arguments = cls.parse(request.path)

        # Traverse down the path and determine to resource we're actually
        # accessing.
        cls = cls.traverse(arguments)

        # Actually construct the resource and return the instance.
        obj = super(ManagedResource, cls).__new__(cls, request, response)

        # Update our instance dictionary with the arugments from `parse`.
        # Note that this adds the 'directives', 'query', 'slug', 'path', and
        # 'extensions' attributes.
        obj.__dict__.update(**arguments)

        if obj.slug:
            # Clean the incoming slug value from the URI, if any.
            obj.slug = obj.meta.slug.clean(obj.slug)
            obj.slug = obj.slug_clean(obj.slug)

        # Return our constructed instance.
        return obj

    @classmethod
    def traverse(cls, arguments):
        """Traverses down the path and determines the accessed resource."""
        # TODO: Implement resource traversal.
        return cls

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

    @property
    def allowed_operations(self):
        """Retrieves the allowed operations for this request."""
        if self.slug is not None:
            return self.meta.detail_allowed_operations

        return self.meta.list_allowed_operations

    def assert_operations(self, *args):
        """Assets if the requested operations are allowed in this context."""
        if not set(args).issubset(self.allowed_operations):
            raise http.exceptions.Forbidden()

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

    @property
    def http_allowed_methods(self):
        if self.slug is None:
            # No slug means that we're accessing this as a list.
            return self.meta.http_list_allowed_methods

        # A slug exists; this is being accessed as an item.
        return self.meta.http_detail_allowed_methods

    def assert_http_allowed_methods(self):
        # No super call as the following replaces it by checking
        # only against the more specific `list_*` or `detail_*` http
        # allowed methods.

        # Check against `list_*` or `detail_*` allowed methods.
        if self.request.method not in self.http_allowed_methods:
            # Current method is found to not be allowed for
            # this type of access; raise.
            raise http.exceptions.MethodNotAllowed(self.http_allowed_methods)

    def get(self):
        """Processes a `GET` request."""
        # Ensure we're allowed to read the resource.
        self.assert_operations('read')

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.slug is not None and not items:
            # Requested a specific resource but nothing is returned.
            raise http.exceptions.NotFound()

        # Build the response object.
        self.make_response(items)

    def read(self):
        """Retrieves data to be displayed; called via GET.

        @returns
            Either a single object or an iterable of objects to be encoded
            and returned to the client.
        """
        # There is no default behavior.
        raise http.exceptions.NotImplemented()

    def create(self, data):
        """Creates the object that is being requested; via POST or PUT.

        @param[in] data
            The data to create the object with.

        @returns
            The object that has been created; or, None, to indicate that no
            object was created.
        """
        # There is no default behavior.
        raise http.exceptions.NotImplemented()

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
        raise http.exceptions.NotImplemented()

    def destroy(self, obj):
        """Destroy the passed object (or objects).

        @param[in] obj
            The objects represented by the current request; the results of
            invoking `self.read()`.

        @returns
            Nothing.
        """
        # There is no default behavior.
        raise http.exceptions.NotImplemented()
