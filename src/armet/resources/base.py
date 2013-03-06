# -*- coding: utf-8 -*-
"""Defines a RESTful resource access protocol.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import os
from collections import Mapping
import hashlib
import logging
from django.db import transaction
import six
import operator
from six import string_types
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.core import urlresolvers
from django.views.decorators.csrf import csrf_exempt
from . import attributes
from . import link
from .attributes import FileAttribute
from .helpers import parent as parent_helper
from .. import utils, http, exceptions, decoders, authorization
from ..query import QueryList


# Get an instance of the logger.
logger = logging.getLogger('armet.resources')


class BaseResource(object):
    """Defines a RESTful resource access protocol for generic resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    #! Name of the resource to use in URIs; defaults to the underscorized
    #! version of the camel cased class name (eg. SomethingHere becomes
    #! something_here).
    name = None

    #! Form class to serve as the recipient of data from the client.
    form = None

    #! List of understood HTTP methods.
    http_method_names = (
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'PATCH',
        'OPTIONS',
        'HEAD',
        'CONNECT',
        'TRACE',
    )

    #! List of allowed HTTP methods.
    http_allowed_methods = (
        'HEAD',
        'GET',
        'POST',
        'PUT',
        'DELETE',
        'OPTIONS',
    )

    #! List of allowed HTTP methods against a whole
    #! resource (eg /user); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_list_allowed_methods = None

    #! List of allowed HTTP methods against a single
    #! resource (eg /user/1); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_detail_allowed_methods = None

    #! List of allowed headers.
    http_allowed_headers = ()

    #! List of allowed HTTP headers against a whole resource (eg /user)
    #! if undeclared or None, will be defaulted to `http_allowed_headers`
    #! in the meta class.
    http_list_allowed_headers = None

    #! List of allowed HTTP headers against a single resource (eg /user/1)
    #! if undeclared or None, will be defaulted to `http_allowed_headers`
    #! in the meta class.
    http_detail_allowed_headers = None

    #! List of exposed headers
    http_exposed_headers = ()

    #! List of exposed HTTP headers against a whole resource (eg /user)
    #! if undeclared or None, will be defaulted to `http_exposed_headers`
    #! in the meta class.
    http_list_exposed_headers = None

    #! List of exposed HTTP headers against a single resource (eg /user/1)
    #! if undeclared or None, will be defaulted to `http_exposed_headers`
    #! in the meta class.
    http_detail_exposed_headers = None

    #! List of allowed operations.
    #! Resource operations are meant to generalize and blur the
    #! differences between "PATCH and PUT", "PUT = create / update",
    #! etc.
    allowed_operations = (
        'read',
        'create',
        'update',
        'destroy',
    )

    #! List of allowed operations against a whole resource.
    #! If undeclared or None, will be defaulted to
    #! `allowed_operations`.
    list_allowed_operations = None

    #! List of allowed operations against a single resource.
    #! If undeclared or None, will be defaulted to `allowed_operations`.
    detail_allowed_operations = None

    #! The only allowed origins for the resource.
    #! Must have something in here if you want to support CORS.
    allowed_origins = ()

    #! List of allowed origins against a whole resource (eg /user)
    #! if undeclared or None, will be defaulted to `allowed_origins`
    #! in the meta class.
    list_allowed_origins = None

    #! List of allowed origins against a single resource (eg /user/1)
    #! if undeclared or None, will be defaulted to `allowed_origins`
    #! in the meta class.
    detail_allowed_origins = None

    #! Mapping of encoders known by this resource.
    encoders = {
        'json': 'armet.encoders.Json',
        # 'xml': 'armet.encoders.Xml',
        'text': 'armet.encoders.Text',
        'yaml': 'armet.encoders.Yaml',
        'bin': 'armet.encoders.Bin',
    }

    #! List of allowed encoders of the understood encoders.
    allowed_encoders = (
        'json',
        # 'xml',
        'text',
        'yaml',
        'bin',
    )

    #! Name of the default encoder of the list of understood encoders.
    default_encoder = 'json'

    #! List of decoders known by this resource.
    decoders = {
        'json': 'armet.decoders.Json',
        'form': 'armet.decoders.Form',
        # 'xml': 'armet.decoders.Xml',
    }

    #! List of allowed decoders of the understood decoders.
    allowed_decoders = (
        'json',
        'form',
        # 'xml',
    )

    #! URL namespace to define the url configuration inside.
    url_name = 'api_view'

    #! Blacklist of attributes to exclude from display.
    exclude = None

    #! Whitelist of attributes to include in the display.
    attributes = None

    #! Additional attributes to include in the display.
    include = None

    #! Whitelist of attributes that are filterable.
    #! Default is to be an empty () which excludes all attributes from filtering.
    #! To have all attributes be eligible for filtering, explicitly specify
    #! `filterable = None` on a resource or any of its parents.
    filterable = None

    #! Authentication protocol(s) to use to authenticate access to
    #! the resource.
    authentication = ('armet.authentication.Authentication',)

    #! Dictionary of the relations for this resource; maps the names of the
    #! attributes to the resources they relate to. The key is the name of the
    #! attribute on the resource; the value is a call to the `resources.relation`
    #! method found in resources.helpers (and imported into resources).
    #!
    #! @example
    #!     relations = {
    #!         'melon': relation('path.to.resource'),
    #!     }
    relations = None

    #! Authorization class for filtering.  Takes a dict of permissions for
    #! CRUD operations.  See the Authorization class for more information on
    #! the parameters this takes.
    authorization = authorization.Authorization()

    #! Hypermedia links to anywhere with some kind of relation type.
    #! NOTE: You should not have to directly add hypermedia relations using
    #!  this links array; this is meant for extensions or advanced usage. For
    #!  normal usage use `relations` to add indirect links to other resources (
    #!  which will result in an added link as well).

    #! Links from the list view of the resource.
    list_links = None

    #! Links from the detail view of the resource.
    detail_links = None

    #! Name used to index into the path cache.
    _cache_path_name = None

    #! Cache of the path to attribute accessor translations.
    _cache_path = {}

    @classmethod
    def make_slug(cls, obj):
        """
        The resource URI segment which is used to access and identify this
        resource.

        @note
            This method is only valid and used if this resource is exposed
            via an urls.py.

        @example
            The following would generate a resource URI (assuming a resource
            name of `MyResource` and a mount of `api`): `/api/MyResource/<pk>`
            @code
                # Use the attribute named 'pk' as the resource URI (default for
                # model resources).
                return obj.pk
        """

    #! The base regex for the urls.
    _url_base_regex = r'^{}{{}}/??(?P<schema>\.schema)?(?:\.(?P<format>[^/]*?))?/?$'

    @utils.classproperty
    @utils.memoize
    def urls(cls):
        """Builds the complete URL configuration for this resource."""
        # Base regex for the url format; includes the `.encoder`
        # functionality.
        regex = cls._url_base_regex.format(cls.name)

        # Simple kwargs so that the URL reverser has some more to go off of
        kwargs = {'resource': cls.name}

        # Collect and return URL patterns
        return patterns('',
            # List access; eg `/poll`
            url(regex.format(''),
                cls.view, name=cls.url_name, kwargs=kwargs),

            # Singular access; eg `/poll/51`
            url(regex.format(r'/(?P<slug>[^/]+?)'),
                cls.view, name=cls.url_name, kwargs=kwargs),

            # Sub access; eg `/poll/1/choices/61/choice_text`
            url(regex.format(r'/(?P<slug>[^/]+?)/(?P<path>.*?)'),
                cls.view, name=cls.url_name, kwargs=kwargs),
        )

    @classmethod
    def schema(cls, format):
        if format == "xml":
            from lxml import etree
            from lxml.builder import ElementMaker

            # Schema namespace
            namespace = "http://www.w3.org/2001/XMLSchema"

            E = ElementMaker(namespace=namespace, nsmap={'xs': namespace})

            # Declare an empty list
            xml = []

            # Iterate through the attributes
            for name, attribute in six.iteritems(cls._attributes):
                if isinstance(attribute, attributes.DateAttribute):
                    xml.append(E.element(name=name, type='xs:date'))
                elif isinstance(attribute, attributes.TimeAttribute):
                    xml.append(E.element(name=name, type='xs:time'))
                elif isinstance(attribute, attributes.DateTimeAttribute):
                    xml.append(E.element(name=name, type='xs:dateTime'))
                elif isinstance(attribute, attributes.NumericalAttribute):
                    xml.append(E.element(name=name, type='xs:integer'))
                elif isinstance(attribute, attributes.BooleanAttribute):
                    xml.append(E.element(name=name, type='xs:boolean'))
                elif isinstance(attribute, attributes.FileAttribute):
                    xml.append(E.element(name=name, type='xs:base64Binary'))
                else:
                    xml.append(E.element(name=name, type='xs:string'))

            # Create the schema
            xsd = E.schema(
                E.element(E.complexType(
                        E.sequence(*xml)
                    ),
                    {'name': cls.name}
                )
            )

            # return the schema in readable format
            return etree.tostring(xsd, pretty_print=True)
        elif format == "yaml" or format == "json":
            import json
            import yaml

            # Declare an empty dictionary
            data = {}

            data[b'type'] = b'//rec'

            # Required as another dictionary
            data[b'required'] = {}

            # Iterate through the elements
            for name, attribute in six.iteritems(cls._attributes):
                if isinstance(attribute, attributes.DateAttribute):
                    data[b'required'][str(name)] = b'//def'
                elif isinstance(attribute, attributes.TimeAttribute):
                    data[b'required'][str(name)] = b'//def'
                elif isinstance(attribute, attributes.DateTimeAttribute):
                    data[b'required'][str(name)] = b'//def'
                elif isinstance(attribute, attributes.NumericalAttribute):
                    data[b'required'][str(name)] = b'//int'
                elif isinstance(attribute, attributes.BooleanAttribute):
                    data[b'required'][str(name)] = b'//bool'
                elif isinstance(attribute, attributes.FileAttribute):
                    data[b'required'][str(name)] = b'//def'
                elif attribute.collection:
                    data[b'required'][str(name)] = b'//arr'
                else:
                    data[b'required'][str(name)] = b'//str'

            return json.dumps(data) if format == "json" else yaml.dump(data,
                default_flow_style=True, explicit_start=True, canonical=False)

        return Exception("Something bad happened ...")

    @classmethod
    @transaction.commit_manually
    @csrf_exempt
    def view(cls, request, *args, **kwargs):
        """
        Entry-point of the request cycle; handles resource creation and
        delegation.
        """
        try:
            # Explode the path if we can.
            if 'path' in kwargs:
                kwargs['path'] = kwargs['path'].split('/')

            # Traverse path segments; determine final resource
            resource = cls.traverse(request, kwargs)

            # Instantiate the resource
            obj = resource(request=request, **kwargs)

            response = None
            if kwargs.get('schema') is not None:
                # Find the name of the determined encoder.
                encoder = obj._determine_encoder()
                for name, value in six.iteritems(obj.encoders):
                    if value is encoder:
                        break

                # Generate the schema for the current resource
                response = http.Response(cls.schema(name),
                    mimetype=encoder.mimetype)

            else:
                # Initiate the dispatch cycle and return its result
                response = obj.dispatch()

                # Commit the database transaction
                cls.commit()

            # Return the dispatched response.
            return response

        except exceptions.Error as ex:
            # Rollback the database transaction.
            cls.rollback()

            # Some known error was thrown before the dispatch cycle; dispatch.
            return ex.dispatch()

        except BaseException:
            # Rollback the database transaction.
            cls.rollback()

            # TODO: Notify system administrator of error

            # Log that an unknown exception occured to help those poor
            # system administrators.
            logger.exception('Internal server error.')

            # Return an empty body indicative of a server failure.
            return http.Response(status=http.client.INTERNAL_SERVER_ERROR)

    @classmethod
    def commit(self):
        """Commit the active transaction.

        The default behavior is to tell django's database layer to commit
        through `django.db.transaction.commit`.
        """
        transaction.commit()

    @classmethod
    def rollback(self):
        """Rollback the active transaction.

        The default behavior is to tell django's database layer to rollback
        through `django.db.transaction.rollback`.
        """
        transaction.rollback()

    @classmethod
    def traverse(cls, request, kwargs):
        """Traverse the resource class with the provided path segments."""
        if not kwargs.get('path') or not kwargs['path'][0]:
            # No sub-resource path provided; return our cls.
            return cls

        # We have at least one segment in the path.
        try:
            # Attempt to get attribute object referenced.
            name = kwargs['path'][0]
            attribute = cls._attributes[name]

        except KeyError:
            # No attribute found for reference; 404.
            raise exceptions.NotFound()

        if not attribute.visible:
            # Field not visible; die.
            raise exceptions.NotFound()

        if attribute.relation is None:
            # No attribute relation defined; a straight access.
            return cls

        # Related attribute.
        # Reduce the path by 1.
        del kwargs['path'][0]

        # Set parent on the object
        kwargs['parent'] = parent = parent_helper(
            resource=cls(
                request=request,
                slug=kwargs.get('slug'),
                parent=kwargs.get('parent'),
                local=kwargs.get('local')),
            name=name,
            related_name=attribute.relation.related_name)

        if attribute.collection and kwargs['path']:
            # Set slug to be the next segment
            kwargs['slug'] = kwargs['path'][0]
            del kwargs['path'][0]

        else:
            if 'slug' in kwargs:
                # No slug; list access.
                del kwargs['slug']

        if attribute.relation.path:
            # There is a path; extend it.
            kwargs['path'] = attribute.relation.path + kwargs['path']

        # Declare if we are local
        kwargs['local'] = attribute.relation.local

        # Find the slug if we need to; let me explain:
        # Take a URI like /poll/41/choices/12/document
        # What slug does this document object have?
        # The only way for us to know is to `.read()` the choices/12 object
        # and ask it what value it has for its document attribute and then
        # ask the document object to make a slug out of it.
        if not kwargs.get('slug'):
            attribute = parent.resource._attributes[parent.name]
            if not attribute.collection and not len(attribute.path) > 1:
                obj = parent.resource.read()
                kwargs['slug'] = cls.make_slug(attribute.accessor(obj))

        # Return the cls object to use
        return attribute.relation.resource.traverse(request, kwargs)

    def __init__(self, **kwargs):
        """Initializes the resources and sets its properites."""
        #! Django WSGI request object.
        self.request = kwargs.get('request')

        #! Identifier of the resource if we are being accessed directly.
        self.slug = kwargs.get('slug')

        #! Explicitly declared format of the request.
        self.format = kwargs.get('format')

        #! Path of the resource.
        self.path = kwargs.get('path')

        if self.path is not None:
            #! Generate a cache name.
            self._cache_path_name = '__'.join(self.path)

        #! Instance of the parent resource (if navigation was resultant of a
        #! relation.
        self.parent = kwargs.get('parent')

        #! Whether internal URIs are local to the parent or not.
        self.local = kwargs.get('local', False)

        # Set some defaults so we can reference this later
        self.encoder = None

        #! A list of query.Query objects representing the query parameters
        self.query = QueryList(self.request.META['QUERY_STRING'])

        #! This is the form instance that is constructed during the clean
        #! and validation cycle.
        self._form = None

    def dispatch(self):
        """
        Performs common work such as authentication, decoding, etc. before
        handing complete control of the result to a function with the
        same name as the request method.
        """
        try:
            # Parse query parameters
            # self.query = query.Query(self.request.META['QUERY_STRING'])

            # Assert authentication and attempt to get a valid user object.
            self.authenticate()

            # Determine the HTTP method; function is now the method function
            # in this resource.
            function = self._determine_method()

            # Detect an appropriate encoder and store it in the resource
            # object for later use.
            self.encoder = self._determine_encoder()

            data = None
            if self.request.body is not None:
                try:
                    # Determine an approparite decoder and decode the
                    # request body.
                    data = self.decode(self.request.body)

                except exceptions.UnsupportedMediaType:
                    # Something happened while decode.
                    if not self.request.body:
                        if self.request.method not in (
                                'GET', 'DELETE', 'HEAD', 'OPTIONS'):
                            # There was a empty body in a request that cares
                            raise

                else:
                    # Run clean cycle over decoded body
                    data = self.clean(data)

            # Delegate to the determined function and return its response.
            return function(data)

        except exceptions.Error as ex:
            # Known error occured; encode it and return the response.
            return ex.dispatch(self.encoder)

    def authenticate(self):
        """Attempts to assert authentication."""
        # Check for cached authentication
        for auth in self.authentication:
            user = auth.authenticate(self.request)
            if user is None:
                # A user object cannot be retrieved with this
                # authn protocol.
                continue

            if user.is_authenticated() or auth.allow_anonymous:
                # A user object has been successfully retrieved.
                self.request.user = user
                break

        else:
            # A user was declared unauthenticated with some confidence.
            raise auth.Unauthenticated

    def make_links(self, data):
        """Builds an iterable of links to serialize in the response."""
        # Get the canonical link
        links = []
        links.append(link.Link(self.url, rel=link.rel.CANONICAL))

        # Serialize link collection for the appropriate end point.
        links.extend(self.detail_links if self.slug else self.list_links)

        if self.slug is not None:
            # Aggregate attribute links.
            # TODO: Ensure attribute proxies are obeyed.
            for name in self._attributes:
                links.append(link.Link(name, rel=link.rel.RELATED, title=name))

        # Return the standard links.
        return links

        #     # Items need the collection links
        #     additional.append(link.Link(self.reverse(
        #         path=self.path, parent=self.parent, local=self.local),
        #         rel=link.rel.COLLECTION))


        # additional = []
        # if self.slug is None:
        #     # Store the item links for use in the link headers.
        #     for item in data:
        #         items.append(link.Link(self.reverse(
        #             slug=self.make_slug(item), path=self.path,
        #             parent=self.parent, local=self.local), rel=link.rel.ITEM))

    def make_response(self, data, status):
        """Builds a response object from the data and status code."""
        # Initialize the response object.
        response = http.Response(status=status)

        # Build the links iterable.
        links = self.make_links(data)

        # Prepare the data for transmission.
        data = self.prepare(data)

        if data is not None:
            # Some kind of data was provided; encode and provide the
            # correct mimetype.
            response.content = self.encoder.encode(data)
            response['Content-Type'] = self.encoder.mimetype
            response['Content-Length'] = len(bytes(response.content))

        # Make an MD5 digest of the content and add it to the response.
        # Use hexdigest so it is actually readable.
        response['Content-MD5'] = hashlib.md5(response.content).hexdigest()

        if links:
            # Only place on the response if we have any links.
            response['Links'] = ','.join(map(str, links))

        # Return the built response.
        return response

    def prepare(self, data):
        """Prepares the data for transmission."""
        if data is None:
            # No data; return nothing.
            return None

        prepare = self.item_prepare
        if not (isinstance(data, string_types) or isinstance(data, Mapping)):
            try:
                # Attempt to prepare each item of the iterable (as long as
                # we're not a string or some sort of mapping).
                return (prepare(x) for x in data)

            except TypeError:
                # Definitely not an iterable.
                pass

        # Prepare just the singular value and return it.
        return prepare(data)

    def generic_prepare(self, obj, name, value):
        relation = self._attributes[name].relation
        if relation is not None:
            # Instantiate a reference to the resource
            try:
                # Attempt to make a slug.
                slug = relation.resource.make_slug(value)

            except AttributeError:
                # Couldn't get the slug.
                slug = None

            resource = relation.resource(request=self.request,
                slug=slug,
                path=relation.path,
                local=relation.local,
                parent=parent_helper(self.__class__(
                        slug=self.make_slug(obj),
                        request=self.request,
                        local=self.local,
                        parent=self.parent),
                    name, relation.related_name))

            if not relation.embed:
                def reverser(value, obj=resource):
                    return obj.reverse(obj.make_slug(value), obj.path,
                        parent=obj.parent, local=obj.local)

                try:
                    # Execute reverser across all values.
                    value = utils.for_all(value, reverser)

                except urlresolvers.NoReverseMatch:
                    # No URL found; force switch to local perhaps ?
                    if not relation.local:
                        raise ImproperlyConfigured(
                            'A resource cannot have a non-local relation to '
                            'another resource that isn\'t publicly exposed.')

            else:
                # We're embedded; inflate
                # Prepare what we have using the related resource
                value = resource.prepare(value)

        # Return whatever we have
        return value

    def item_prepare(self, item):
        """Prepares an item for transmission."""
        # Initialize the object that will hold the item.
        obj = {}

        if self.path:
            if self._cache_path_name not in self._cache_path:
                # No path attribute has been created yet; create one
                path_field_cls = self._attributes[self.path[0]].__class__
                self._cache_path[self._cache_path_name] = path_field_cls(self,
                    path=self.path)

            # Retrieve the cached path: (attribute, segment#0)
            path_field = self._cache_path.get(self._cache_path_name)

        # Iterate through the attributes and build the object from the item.
        for name, attribute in six.iteritems(self._attributes):
            if not attribute.visible:
                # Field is not visible on the response object.
                continue

            if self.path and self.path[0] != name:
                # Not what we are looking for; go away.
                continue

            try:
                # Apply the attribute accessor and request the value of the item.
                value = attribute.accessor(item)

            except KeyError:
                # Field not found.. okay.
                raise exceptions.NotFound()

            # Set value on object after preparing it
            obj[name] = attribute.prepare(self, item, value)

        if self.path and path_field:
            try:
                # Navigate through some hoops to return from what we construct.
                # Utilize the attribute accessor to resolve the resource path.
                obj = path_field.accessor(obj)

            except (IndexError, ValueError, AttributeError, TypeError):
                # Something weird happened with a path segment.
                raise exceptions.NotFound()

        # Return the resultant object.
        return obj

    def item_clean(self, item):
        """Performs the micro-clean cycle over an item using its attribute."""
        for name in item:
            # Attempt to get a field from the item name
            field = self._attributes.get(name)

            if field is not None:
                # Invoke the micro-clean cycle on the field for this value
                item[name] = field.clean(item[name])

        # Return our primed object.
        return item

    def relation_clean(self, value):
        """Normalizes relation accessors."""
        # TODO: Allow exploded objects here; would need to pass these
        #   off to the creation method of the related class.
        try:
            # Attempt to resolve the relation reference.
            return self.resolve(value)

        except ValueError:
            # Must be already resolved (or something weird)
            return value

    def clean(self, data):
        """Cleans data from the request for processing."""
        # Before even the micro-clean cycle; things need to happen to make
        # the data more pythonic and less dumb as decoders are just that,
        # dumb.
        for name, attribute in six.iteritems(self._attributes):
            value = data.get(name)
            if value is not None:
                if attribute.relation is not None:
                    # Resolve relation URIs (eg. /resource/:slug/) if we
                    # need to.
                    data[name] = self.relation_clean(value)

            elif attribute.collection and attribute.editable:
                # No value at all but the value is a collection; set an
                # empty iterable.
                data[name] = ()

        if isinstance(data, collections.Sequence):
            # Invoke the micro-clean cycle on all objects passed.
            data = [self.item_clean(item) for item in data]

        else:
            # Not a list; do a singular object.
            data = self.item_clean(data)

        # Split data items and files; this process also removes all data
        # that we do not understand; ie. extra fields passed.
        items, files = {}, {}
        for name, value in six.iteritems(data):
            attribute = self._attributes.get(name)
            if attribute is not None:
                if isinstance(attribute, FileAttribute):
                    # Value is supposed to be a file object
                    files[name] = value

                else:
                    # Value is something more normal
                    items[name] = value

        if not files:
            # Files were empty; so explicitly set to None so the form
            # doesn't get confused.
            files = None

        if self.form is not None:
            # Instantiate form using provided data (if form exists).
            self._form = self.form(data=items, files=files)

            # Ensure the form is valid and if not; throw a 400
            if not self._form.is_valid():
                raise exceptions.BadRequest(self._form.errors)

            # Return the cleaned data that should be sanitized, etc.
            return self._form.cleaned_data

        else:
            # No form to do the dirty work; we need to merge items and files
            # ourselves
            items.update(files or {})
            return items

    def filter(self, iterable):
        """Filters and returns the iterable.  Implemented as a no-op in the
        base class.
        """
        return iterable

    def sort(self, data):
        """Sorts and returns the data.
        """
        for parameter in self.query:
            direction = parameter.direction
            # Short circuit the sort
            if direction is None:
                continue

            # Get a callable that will return the proper lookup
            attr = operator.attrgetter(query.LOOKUP_SEP.join(parameter.path))

            # Do the actual sorting
            if direction == 'asc':
                data = sorted(data, attr=attr, reverse=True)
            else:
                data = sorted(data, attr=attr)

        return data

    #! Identifier to access the resource URL as a whole.
    _URL = 2

    #! Identifier to access the resource individualy.
    _URL_SLUG = 1

    #! Identifier to access the resource individualy with a path.
    _URL_PATH = 0

    @classmethod
    @utils.memoize
    def _url_format(cls, identifier):
        """Gets the string format for a URL for this resource."""
        # HACK: This is a hackish way to get a string format representing
        #       the URL that would have been reversed with `reverse`. Speed
        #       increases of ~192%. Proper way would be a django internal
        #       function to just do the url reversing `halfway` but we'll
        #       see if that can make it in.
        # TODO: Perhaps move this and the url reverse speed up bits out ?
        try:
            urlmap = cls._resolver.reverse_dict.getlist(
                cls.view)[identifier][0][0]

        except IndexError:
            # No found reversal; die
            raise urlresolvers.NoReverseMatch()

        url = urlmap[0]
        for param in urlmap[1]:
            url = url.replace('({})'.format(param), '')

        return '{}{}'.format(cls._prefix, url)

    @property
    def url(self):
        """Retrieves the reversed URL for this resource instance."""
        return self.reverse(self.slug, self.path, self.parent, self.local)

    def resolve(self, url):
        """Resolves a url into its corresponding view by proxying to the
        django url resolver.
        """
        # Django cannot resolve urls that begin with a site prefix.
        # For sites that are not mounted on root,
        # slice off the site prefix if one exists.
        # Will replace "/" with "/" if that's the prefix.
        stripped = url.replace(urlresolvers.get_script_prefix(), '/')

        try:
            # Get the actual resource.
            resolved = urlresolvers.resolve(stripped)

        except urlresolvers.Resolver404:
            # Raise a normal exception here.
            raise ValueError('No resolution found.')

        # Rip out the class and kwargs from it.
        klass = resolved.func.__self__
        kw = resolved.kwargs

        # Instantiate and read that class,
        # returning whatever object is at that resource.
        obj = klass(request=self.request, **kw)
        obj._assert_operation('read')
        return obj.read()

    @classmethod
    def reverse(cls, slug=None, path=None, parent=None, local=False):
        """Reverses a URL for the resource or for the passed object.

        @param[in] parent
            Describes where to reverse this resource from.
            Tuple of (<parent resource>, "attribute name on parent").
        """
        # NOTE: Not using `iri_to_uri` here; therefore only ASCII is permitted.
        #       Need to look into this later so we can have unicode here.
        if local and parent is not None:
            # Local path; we need to do something about it.
            # The parent must be a specific parent; ie. with a slug

            # Build composite path
            composite = []
            composite.append(parent.name)

            if (slug is not None
                    and parent.resource._attributes[parent.name].collection):
                composite.append(slug)

            if path is not None:
                composite.extend(path)

            # Send it off to the parent object for reversal.
            return parent.resource.reverse(parent.resource.slug, composite,
                parent=parent.resource.parent, local=parent.resource.local)

        if slug is None:
            # Accessing the resource as a whole; no path is possible.
            return cls._url_format(cls._URL)

        if path:
            # Accessing the resource individually with a path.
            return cls._url_format(cls._URL_PATH) % (slug, os.path.join(*path))

        # Accessing the resource individually without a path.
        return cls._url_format(cls._URL_SLUG) % slug

    def options(self, data=None):
        """Process a `OPTIONS` request.

        @param[in] data
            The body of the request; unused in a normal `OPTIONS`.

        @returns
            The HTTPResponse object to return to the client.
        """
        response = http.Response(status=http.client.OK)

        # Step 1
        # Check for Origin header.
        origin = self.request.META.get('ORIGIN')
        if not origin:
            return response

        # Step 2
        # Check if the origin is in the list of allowed origins.
        if not (origin in self._allowed_origins or
                '*' in self._allowed_origins):
            return response

        # Step 3
        # Try to parse the Request-Method header if it exists.
        method = self.request.META.get('ACCESS_CONTROL_REQUEST_METHOD')
        if not method or method not in self.http_method_names:
            return response

        # Step 4
        # Try to parse the Request-Header header if it exists.
        headers = self.request.META.get('ACCESS_CONTROL_REQUEST_HEADERS', ())
        # Need to check parsing here.

        # Step 5
        # Check if the method is allowed on this resource.
        if method not in self._allowed_methods:
            return response

        # Step 6
        # Check if the headers is allowed on this resource.
        # This needs to be case insensitive.
        allowed_headers = [header.lower() for header in self._allowed_headers]
        if any(header.lower() not in allowed_headers for header in headers):
            return response

        # Step 7
        # Always add the origin.
        response['Access-Control-Allow-Origin'] = origin
        # Check if we can provide credentials.
        if self.authentication:
            response['Access-Control-Allow-Credentials'] = 'true'

        # Step 8
        # Optionally add Max-Age header.

        # Step 9
        # Add the allowed methods.
        allowed_methods = ','.join(self._allowed_methods)
        response['Access-Control-Allow-Methods'] = allowed_methods

        # Step 10
        # Add any allowed headers.
        allowed_headers = ','.join(self._allowed_headers)
        if allowed_headers:
            response['Access-Control-Allow-Headers'] = allowed_headers

        # Return the response with our new headers applied.
        return response

    def head(self, data=None):
        """Process a `HEAD` request.

        @param[in] data
            The body of the request; unused in a normal `HEAD`.

        @returns
            The HTTPResponse object to return to the client.
        """
        # Run through a get as if that was the real method.
        response = self.get(data)

        # Clear the body. Setting `content` auto-sets the length to 0.
        response.body = None

        # Return our response generated by the `GET`.
        return response

    def delete(self, data=None):
        """Processes a `DELETE` request.

        @param[in] data
            The body of the request; unused in a normal `DELETE`.

        @returns
            The HTTPResponse object to return to the client.
        """
        # Ensure we're allowed to perform this operation.
        self._assert_operation('destroy')

        # Check if the resource exists.
        items = self.read()

        # Ensure we're authorized to delete this.
        if self.authorization.is_authorized(
                self.request.user, 'destroy', self, items):
            raise exceptions.Forbidden()

        if not items:
            # Requested a specific resource but no resource was returned.
            raise exceptions.NotFound()

        # If it's there, destroy it.
        self.destroy(items)

        # Return the response
        return self.make_response(None, http.client.NO_CONTENT)

    def put(self, data=None):
        """Processes a `PUT` request.

        @param[in] data
            The body of the request; unused in a normal `PUT`.

        @returns
            The HTTPResponse object to return to the client.
        """
        if self.slug is None:
            # We don't implement list PUT yet.
            raise exceptions.NotImplemented()

        else:
            # Read in the current object.
            obj = self.read()

            # Ensure we're authorized to delete this.
            if self.authorization.is_authorized(
                    self.request.user, 'update', self, obj):
                raise exceptions.Forbidden()

            # Ensure we're authorized to create this.
            if self.authorization.is_authorized(
                    self.request.user, 'update', self, self._form.instance):
                raise exceptions.Forbidden()

            # Delegate to the `update` function to actually update the object.
            response = self.update(obj, data)

        # Build and return the response object
        return self.make_response(response, http.client.OK)

    def get(self, data=None):
        """Processes a `GET` request.

        @param[in] data
            The body of the request; unused in a normal `GET`.

        @returns
            The HTTPResponse object to return to the client.
        """
        # Ensure we're allowed to perform this operation.
        self._assert_operation('read')

        # Delegate to `read` to retrieve the items.
        items = self.read()

        if self.slug is not None:
            if not items:
                # Requested a specific resource but no resource was returned.
                raise exceptions.NotFound()

            if not isinstance(items, six.string_types):
                try:
                    # Ensure we return only a single object if we were
                    # requested to return such.
                    items = items[0]

                except (TypeError, KeyError):
                    # Whatever; assume we're just one I guess.
                    pass

        else:
            if items is None:
                # Ensure we at least have an empty list
                items = []

        # Build and return the response object
        return self.make_response(items, http.client.OK)

    def post(self, data):
        """Processes a `POST` request.

        @param[in] data
            The body of the request after going being decoded and subsequently
            cleaned by the form.

        @returns
            The HTTPResponse object to return to the client.
        """
        # Ensure we're allowed to create
        self._assert_operation('create')

        # Ensure we're authorized to create this.
        if self.authorization.is_authorized(
                self.request.user, 'create', self, self._form.instance):
            raise exceptions.Forbidden()

        if self.slug is None:
            # Set our initial status code
            status = http.client.CREATED

            # Delegate to the `create` function to actually create the
            # object.
            response = self.create(data)

        else:
            # We don't implement object POST.
            # TODO: Figure out something to do here I suppose?
            raise exceptions.NotImplemented()

        # Build and return the response object
        return self.make_response(response, status)

    @property
    def _allowed_methods(self):
        """Retrieves a list of allowed HTTP methods for the current request."""
        return (self.http_detail_allowed_methods if self.slug is not None else
            self.http_list_allowed_methods)

    @property
    def _allowed_headers(self):
        """Retrieves a list of allowed headers for the current request."""
        return (self.http_detail_allowed_headers if self.slug is not None else
            self.http_list_allowed_headers)

    @property
    def _exposed_headers(self):
        """Retrieves a list of exposed headers for the current request."""
        return (self.http_detail_exposed_headers if self.slug is not None else
            self.http_list_exposed_headers)

    @property
    def _allowed_origins(self):
        """Retrieves a list of allowed origins for the current request."""
        return (self.detail_allowed_origins if self.slug is not None else
            self.list_allowed_origins)

    def _determine_method(self):
        """Determine the HTTP method being used and if it is acceptable."""
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in self.request.META:
            # Someone is using a client that isn't smart enough to send proper
            # verbs; but can still send headers.
            self.request.method = self.request.META[
                'HTTP_X_HTTP_METHOD_OVERRIDE'].upper()

        if self.request.method not in self.http_method_names:
            # Method not understood by our library; die.
            raise exceptions.NotImplemented()

        methods = self._allowed_methods
        if self.request.method not in methods:
            # Method is not in the list of allowed HTTP methods for this
            # access of the resource.
            raise exceptions.MethodNotAllowed(', '.join(methods).strip())

        function = getattr(self, self.request.method.lower(), None)
        if function is None:
            # Method understood and allowed but not implemented; stupid us.
            raise exceptions.NotImplemented()

        # Method is just fine; toss 'er back.
        return function

    def _determine_encoder(self):
        """Determine the encoder to use according to the request object."""
        accept = self.request.META.get('HTTP_ACCEPT', '*/*')
        if self.format is not None:
            # An explicit form was supplied; attempt to get it directly
            name = self.format.lower()
            if name in self.allowed_encoders:
                encoder = self.encoders.get(name)
                if encoder is not None and encoder.can_transcode(accept):
                    # Found an appropriate encoder.
                    return encoder

        elif accept.strip() != '*/*':
            # No format specified at the URL; iterate through encoders
            # to try and match one.
            for name in self.allowed_encoders:
                encoder = self.encoders[name]
                if encoder.can_transcode(accept):
                    # Found an appropriate encoder; we're done
                    return encoder

        else:
            # Neither `.fmt` nor an accept header was specified
            return self.encoders.get(self.default_encoder)

        # Failed to find an appropriate encoder
        # Get dictionary of available formats
        available = {}
        for name in self.allowed_encoders:
            available[name] = self.encoders[name].mimetype

        # Encode the response using the appropriate exception
        raise exceptions.NotAcceptable(available)

    def decode(self, body):
        """
        Determine the decoder to use according to the request object and then
        subsequently decode the request body.
        """
        # Attempt to get the content-type.
        content_type = self.request.META.get('CONTENT_TYPE')

        if content_type is not None:
            # Attempt to find an encoder that matches the media type
            # presented.
            for decoder in six.itervalues(self.decoders):
                if decoder.can_transcode(content_type):
                    # Good; get out.
                    break

            else:
                # Some unknown content type was presented; throw up our hands.
                raise exceptions.UnsupportedMediaType()

            try:
                # Decode and return the request body
                return decoder.decode(self.request, self._attributes)

            except decoders.DecoderError:
                # No dice; we don't understand it.
                raise exceptions.UnsupportedMediaType()

        # No content type header was presented; attempt to decode using
        # all available decoders.
        for decoder in six.itervalues(self.decoders):
            try:
                # Attemp to decode and return the body.
                return decoder.decode(self.request, self._attributes)

            except decoders.DecoderError:
                # An error occured; continue on to the next decoder.
                pass

        # We have no idea what we've received.
        raise exceptions.UnsupportedMediaType()

    @property
    def _allowed_operations(self):
        """Retrieves a list of allowed operations for the current request."""
        return (self.detail_allowed_operations if self.slug is not None else
            self.list_allowed_operations)

    def _assert_operation(self, operation):
        """Determine if the requested operation is allowed in this context."""
        # Check if the operation is accessible.
        if not self.authorization.is_accessible(
                self.request.user, operation, self):
            # If a resource is not accessible then we return 404 as the
            #   resource in its entirety is hidden from this user.
            raise exceptions.NotFound()

        # Check if the operation is allowed.
        if operation not in self._allowed_operations:
            # Assert conditiion and bail.
            raise exceptions.Forbidden(data)

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
