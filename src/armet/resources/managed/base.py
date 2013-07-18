# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import logging
from collections import Sequence
from armet import http
from armet.resources.resource import base


logger = logging.getLogger(__name__)


class ManagedResource(base.Resource):
    """Implements the RESTful resource protocol for managed resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.ManagedResource` (defined in
        the `__init__.py`).
    """

    class Meta:
        # The managed resource access pattern.
        # Traversal is handled a bit more dyanmically than allowed with
        # the simple pattern syntax.
        patterns = [
            r'^'
            r'(?:\:(?P<directives>[^/\(\)]*))?'
            r'(?:\((?P<query>[^/]*)\))?'
            r'(?:/(?P<slug>[^/]+?))?'
            r'(?:/(?P<path>.+?))??'
            r'(?:\.(?P<extensions>[^/]+?))??/??$'
        ]

    #! An ordered dictionary of attributes that are gathered from both
    #! the metaclass and attributes defined directly on the resource.
    #!
    #! Attributes may be declared in a few different
    #! ways. The next few code blocks are identical in function.
    #!
    #! @code
    #! from armet import resources
    #!
    #! class Resource(resources.Resource):
    #!     name = resources.Attribute()
    #!     created = resources.Attribute('created')
    #! @endcode
    #!
    #! @code
    #! from armet import resources
    #!
    #! class Resource(resources.Resource):
    #!     class Meta:
    #!         include = {
    #!             'name': resources.Attribute()
    #!             'created': resources.Attribute('created')
    #!         }
    #! @endcode
    #!
    #! @code
    #! from armet import resources
    #!
    #! class Resource(resources.Resource):
    #!     class Meta:
    #!         include = {
    #!             'name': None,
    #!             'created': 'created'
    #!         }
    #! @endcode
    #!
    #! @code
    #! from armet import resources
    #!
    #! class Resource(resources.Resource):
    #!     class Meta:
    #!         include = ('name',)
    #!
    #!     created = resources.Attribute('created')
    #! @endcode
    attributes = None

    #! The slug that is used to identify the resource an item is being
    #! requested. None if a list is being requested.
    slug = None

    @classmethod
    def parse(cls, path):
        result = super(ManagedResource, cls).parse(path)
        if result:
            # Found something; parse the result.
            resource, data, end = result

            # Normalize the list arguments.
            for sep, name in (('.', 'extensions'), (':', 'directives')):
                if data[name]:
                    data[name] = data[name].split(sep)

                else:
                    data[name] = []

            # Reset the result.
            result = resource, data, end

        # Return what we got.
        return result

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

    def make_response(self, data=None, status=http.client.OK):
        """Fills the response object from the passed data."""
        if data is not None:
            # Prepare the data for transmission.
            data = self.prepare(data)

            # Encode the data using a desired encoder.
            self.response.write(data, serialize=True)

        # Make sure that the status code is set.
        self.response.status = status

    def prepare(self, data):
        if data is None:
            # No data; return nothing.
            return None

        if (not isinstance(data, six.string_types)
                and isinstance(data, Sequence)):
            # Attempt to prepare each item of the iterable (as long as
            # we're not a string or some sort of mapping).
            for index, value in enumerate(data):
                data[index] = self.item_prepare(data[index])

            return data

        # Prepare just the singular value and return.
        return self.item_prepare(data)

    def item_prepare(self, item):
        # Initialize the object that hold the resultant item.
        obj = {}

        # Iterate through the attributes and build the object from the item.
        for name, attribute in self.attributes.items():
            if attribute.include:
                # Run the attribute through its prepare cycle.
                obj[name] = attribute.prepare(
                    # Optional preparation cycle on the resource.
                    self.preparers[name](
                        # Retrieves the value from the object.
                        self, item, attribute.get(item)))

        # Return the resultant object.
        return obj

    def clean(self, data):
        if not data:
            # If no data; return an empty object.
            return {}

        if (not isinstance(data, six.string_types)
                and isinstance(data, Sequence)):
            # Attempt to clean each item of the iterable (as long as
            # we're not a string or some sort of mapping).
            for index, value in enumerate(data):
                data[index] = self.item_clean(data[index])

            return data

        # Clean just the singular value and return.
        return self.item_clean(data)

    def item_clean(self, item):
        # Initialize the object that hold the resultant item.
        obj = {}

        # Iterate through the attributes and build the object from the item.
        for name, attribute in self.attributes.items():
            if attribute.include:
                # Run the attribute through its prepare cycle.
                obj[name] = self.cleaners[name](
                    # Micro preparation cycle on the attribute object.
                    self, attribute.clean(item.get(name)))

        # Return the resultant object.
        return obj

    @property
    def http_allowed_methods(self):
        if self.slug is None:
            # No slug means that we're accessing this as a list.
            return self.meta.http_list_allowed_methods

        # A slug exists; this is being accessed as an item.
        return self.meta.http_detail_allowed_methods

    def assert_http_allowed_methods(self, request):
        # No super call as the following replaces it by checking
        # only against the more specific `list_*` or `detail_*` http
        # allowed methods.

        # Check against `list_*` or `detail_*` allowed methods.
        if request.method not in self.http_allowed_methods:
            # Current method is found to not be allowed for
            # this type of access; raise.
            raise http.exceptions.MethodNotAllowed(self.http_allowed_methods)

    def get(self, request, response):
        """Processes a `GET` request."""
        # Ensure we're allowed to read the resource.
        self.assert_operations('read')

        try:
            # Delegate to `read` to retrieve the items.
            items = self.read()

        except AttributeError:
            # No read method defined.
            raise http.exceptions.NotImplemented()

        if self.slug is not None and not items:
            # Requested a specific resource but nothing is returned.
            raise http.exceptions.NotFound()

        # Build the response object.
        self.make_response(items)

    def post(self, request, response):
        """Processes a `POST` request."""
        if self.slug is not None:
            # Don't know what to do an item access.
            raise http.exceptions.NotImplemented()

        # Ensure we're allowed to create a resource.
        self.assert_operations('create')

        # Deserialize and clean the incoming object.
        data = self.clean(self.request.read(deserialize=True))

        try:
            # Delegate to `create` to create the item.
            item = self.create(data)

        except AttributeError:
            # No read method defined.
            raise http.exceptions.NotImplemented()

        # Build the response object.
        self.make_response(item, status=http.client.CREATED)

    def put(self, request, response):
        """Processes a `PUT` request."""
        if self.slug is None:
            # Mass-PUT is not implemented.
            raise http.exceptions.NotImplemented()

        try:
            # Check if the resource exists.
            target = self.read()

        except AttributeError:
            # No read method defined.
            raise http.exceptions.NotImplemented()

        # Deserialize and clean the incoming object.
        data = self.clean(self.request.read(deserialize=True))

        if target is not None:
            # Ensure we're allowed to update the resource.
            self.assert_operations('update')

            try:
                # Delegate to `update` to create the item.
                self.update(target, data)

            except AttributeError:
                # No read method defined.
                raise http.exceptions.NotImplemented()

            # Build the response object.
            self.make_response(target, status=http.client.OK)

        else:
            # Ensure we're allowed to create the resource.
            self.assert_operations('create')

            try:
                # Delegate to `create` to create the item.
                target = self.create(data)

            except AttributeError:
                # No read method defined.
                raise http.exceptions.NotImplemented()

            # Build the response object.
            self.make_response(target, status=http.client.CREATED)

    def delete(self, request, response):
        """Processes a `DELETE` request."""
        if self.slug is None:
            # Mass-DELETE is not implemented.
            raise http.exceptions.NotImplemented()

        # Ensure we're allowed to destroy a resource.
        self.assert_operations('destroy')

        try:
            # Delegate to `destroy` to destroy the item.
            self.destroy()

        except AttributeError:
            # No read method defined.
            raise http.exceptions.NotImplemented()

        # Build the response object.
        self.make_response(status=http.client.NO_CONTENT)
