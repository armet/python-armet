# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import logging
from collections import Sequence, MutableSequence, Iterable
from armet import http, pagination
from armet.exceptions import ValidationError
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

    #! An ordered dictionary of attributes that are gathered from
    #! attributes defined directly on the resource.
    #!
    #! @code
    #! from armet import resources
    #!
    #! class Resource(resources.Resource):
    #!     name = resources.Attribute()
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

    def __init__(self, *args, **kwargs):
        super(ManagedResource, self).__init__(*args, **kwargs)

        #! Map of errors that have occurred in the clean cycle.
        self._errors = {}

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

    def make_response(self, data=None):
        """Fills the response object from the passed data."""
        if data is not None:
            # Prepare the data for transmission.
            data = self.prepare(data)

            # Encode the data using a desired encoder.
            self.response.write(data, serialize=True)

    def prepare(self, data):
        if data is None:
            # No data; return nothing.
            return None

        if self.path:
            # Ensure we are dealing with only one segment.
            if '/' in self.path:
                raise http.exceptions.NotFound()

        if (isinstance(data, Iterable)
                and not isinstance(data, six.string_types)):
            # Resolve the sequence only if we need to.
            if not isinstance(data, MutableSequence):
                data = list(data)

            # Attempt to prepare each item of the iterable (as long as
            # we're not a string or some sort of mapping).
            for index, value in enumerate(data):
                data[index] = self.item_prepare(data[index])

            return data

        # Prepare just the singular value and return.
        data = self.item_prepare(data)
        if data is None:
            raise http.exceptions.NotFound()

        return data

    def attribute_prepare(self, name, attribute, item):
        # Run the attribute through its prepare cycle.
        return attribute.prepare(
            # Optional preparation cycle on the resource.
            self.preparers[name](
                # Retrieves the value from the object.
                self, item, attribute.get(item)))

    def item_prepare(self, item):
        # Check for a path first.
        if self.path:
            attribute = self.attributes.get(self.path)
            if attribute is None:
                raise http.exceptions.NotFound()

            if not attribute.read:
                raise http.exceptions.Forbidden()

            return self.attribute_prepare(self.path, attribute, item)

        # Initialize the object that hold the resultant item.
        obj = {}

        # Iterate through the attributes and build the object from the item.
        for name, attribute in self.attributes.items():
            if attribute.include:
                # Run the attribute through its prepare cycle.
                obj[attribute.name] = self.attribute_prepare(
                    name, attribute, item)

        # Return the resultant object.
        return obj

    def _clean(self, target, data):
        # Wrap clean so that it can be extended and have validation
        # errors properly handled.

        # HACK: Replace this later with passing item down through clean(...) --
        # however this is to fix a bug and should not break the API.
        self.__target = target

        try:
            data = self.clean(data)

        except AssertionError as ex:
            self._errors['__all__'] = [str(ex)]

        except ValidationError as ex:
            self._errors['__all__'] = ex.errors

        if self._errors:
            # Collect errors and raise a BadRequest message to the client.
            raise http.exceptions.BadRequest(self._errors)

        return data

    def clean(self, data):
        if not data:
            # If no data; just alias it to an empty dictionary.
            data = {}

        if (isinstance(data, Sequence)
                and not isinstance(data, six.string_types)):
            # Attempt to clean each item of the iterable (as long as
            # we're not a string or some sort of mapping).
            for index, value in enumerate(data):
                data[index] = self.item_clean(data[index])

            return data

        # Clean just the singular value and return.
        return self.item_clean(data)

    def item_clean(self, item):
        # Iterate through the attributes and build the object from the item.
        obj = {}

        for name, attribute in self.attributes.items():
            value = item.get(attribute.name)

            try:
                if value is not None:
                    # Run the attribute through its clean cycle.
                    value = self.cleaners[name](
                        # Micro preparation cycle on the attribute object.
                        self, attribute.clean(value))

                    # Check if this attribute is writeable.
                    if not attribute.write:
                        if (not self.__target
                                or attribute.get(self.__target) != value):
                            raise ValidationError('Attribute is read-only.')

                # Ensure that we don't have a null or it is provided.
                if value is None:
                    if name in item and not attribute.null:
                        raise ValidationError('Must not be null.')

                    if name not in item and attribute.required:
                        raise ValidationError('Must be provided.')

            except AssertionError as ex:
                self._errors[attribute.name] = [str(ex)]
                value = None

            except ValidationError as ex:
                self._errors[attribute.name] = ex.errors
                value = None

            obj[name] = value

        return obj

    @property
    def http_allowed_methods(self):
        if self.slug is None:
            # No slug means that we're accessing this as a list.
            return self.meta.http_list_allowed_methods

        # A slug exists; this is being accessed as an item.
        return self.meta.http_detail_allowed_methods

    def require_http_allowed_method(self, request):
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

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.slug is not None and not items:
            # Requested a specific resource but nothing is returned.

            # Attempt to resolve by changing what we understand as
            # a slug to a path.
            self.path = self.path + self.slug if self.path else self.slug
            self.slug = None

            # Attempt to retreive the resource again.
            items = self.read()

            # Ensure that if we have a slug and still no items that a 404
            # is rasied appropriately.
            if not items:
                raise http.exceptions.NotFound()

        if (isinstance(items, Iterable)
                and not isinstance(items, six.string_types)) and items:
            # Paginate over the collection.
            items = pagination.paginate(self.request, self.response, items)

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
        data = self._clean(None, self.request.read(deserialize=True))

        # Delegate to `create` to create the item.
        item = self.create(data)

        # Build the response object.
        self.response.status = http.client.CREATED
        self.make_response(item)

    def put(self, request, response):
        """Processes a `PUT` request."""
        if self.slug is None:
            # Mass-PUT is not implemented.
            raise http.exceptions.NotImplemented()

        # Check if the resource exists.
        target = self.read()

        # Deserialize and clean the incoming object.
        data = self._clean(target, self.request.read(deserialize=True))

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
            self.make_response(target)

        else:
            # Ensure we're allowed to create the resource.
            self.assert_operations('create')

            # Delegate to `create` to create the item.
            target = self.create(data)

            # Build the response object.
            self.response.status = http.client.CREATED
            self.make_response(target)

    def delete(self, request, response):
        """Processes a `DELETE` request."""
        if self.slug is None:
            # Mass-DELETE is not implemented.
            raise http.exceptions.NotImplemented()

        # Ensure we're allowed to destroy a resource.
        self.assert_operations('destroy')

        # Delegate to `destroy` to destroy the item.
        self.destroy()

        # Build the response object.
        self.response.status = http.client.NO_CONTENT
        self.make_response()
