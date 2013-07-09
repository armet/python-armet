# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import logging
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

    # def __new__(cls, request, response):
    #     # Parse any arguments out of the path.
    #     arguments = cls.parse(request.path)

    #     # Traverse down the path and determine to resource we're actually
    #     # accessing.
    #     cls = cls.traverse(arguments)

    #     # Actually construct the resource and return the instance.
    #     obj = super(ManagedResource, cls).__new__(cls)

    #     # Update our instance dictionary with the arugments from `parse`.
    #     # Note that this adds the 'directives', 'query', 'slug', 'path', and
    #     # 'extensions' attributes.
    #     obj.__dict__.update(**arguments)

    #     # Return our constructed instance.
    #     return obj

    #! Precompiled regular expression used to parse out the path.
    # _parse_pattern = re.compile(
    #     r'^'
    #     r'(?:\:(?P<directives>[^/\(\)]*))?'
    #     r'(?:\((?P<query>[^/]*)\))?'
    #     r'(?:/(?P<slug>[^/]+?))?'
    #     r'(?:/(?P<path>.+?))??'
    #     r'(?:\.(?P<extensions>[^/]+?))??/??$')

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

    # @classmethod
    # def parse(cls, path=''):
    #     """Parses out parameters and separates them out of the path."""
    #     # Apply the compiled regex.
    #     arguments = re.match(cls._parse_pattern, path).groupdict()

    #     # Explode the list arguments; they should be represented as
    #     # empty arrays and not None.
    #     if arguments['extensions']:
    #         arguments['extensions'] = arguments['extensions'].split('.')

    #     else:
    #         arguments['extensions'] = []

    #     if arguments['directives']:
    #         arguments['directives'] = arguments['directives'].split(':')

    #     else:
    #         arguments['directives'] = []

    #     # Return the arguments
    #     return arguments

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
        self.response.write(data, serialize=True)

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
            for index, value in enumerate(data):
                data[index] = self.item_prepare(data[index])

            return data

        # Prepare just the singular value and return.
        return self.item_prepare(data)

    def item_prepare(self, item):
        """Prepares a single item for encoding."""
        # Initialize the object that hold the resultant item.
        obj = {}

        # Iterate through the attributes and build the object from the item.
        for name, attribute in self.attributes.items():
            if attribute.include:
                # Run the attribute through its prepare cycle.
                obj[name] = self.preparers[name](
                    # Micro preparation cycle on the attribute object.
                    self, item, attribute.prepare(
                        # Retrieves the value from the object.
                        attribute.get(item)))

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

    # def read(self):
    #     """Retrieves data to be displayed; called via GET.

    #     @returns
    #         Either a single object or an iterable of objects to be encoded
    #         and returned to the client.
    #     """
    #     # There is no default behavior.
    #     raise http.exceptions.NotImplemented()

    # def create(self, data):
    #     """Creates the object that is being requested; via POST or PUT.

    #     @param[in] data
    #         The data to create the object with.

    #     @returns
    #         The object that has been created; or, None, to indicate that no
    #         object was created.
    #     """
    #     # There is no default behavior.
    #     raise http.exceptions.NotImplemented()

    # def update(self, obj, data):
    #     """Updates the object that is being requested; via PATCH or PUT.

    #     @param[in] obj
    #         The objects represented by the current request; the results of
    #         invoking `self.read()`.

    #     @param[in] data
    #         The data to update the object with.

    #     @returns
    #         The object that has been updated.
    #     """
    #     # There is no default behavior.
    #     raise http.exceptions.NotImplemented()

    # def destroy(self, obj):
    #     """Destroy the passed object (or objects).

    #     @param[in] obj
    #         The objects represented by the current request; the results of
    #         invoking `self.read()`.

    #     @returns
    #         Nothing.
    #     """
    #     # There is no default behavior.
    #     raise http.exceptions.NotImplemented()
