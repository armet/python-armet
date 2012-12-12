# -*- coding: utf-8 -*-
"""Defines a RESTful resource access protocol.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import collections
import os
from collections import Mapping
import logging
import six
import operator
from six import string_types
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.core import urlresolvers
from django.views.decorators.csrf import csrf_exempt
from . import attributes, helpers
from .. import utils, http, exceptions, decoders, authorization, query


# Get an instance of the logger.
logger = logging.getLogger('armet.resources')


class BaseResource(object):
    """Defines a RESTful resource access protocol for generic resources.

    @note
        This is not the class to derive from when implementing your own
        resources. Derive from `armet.resources.Resource` (defined in
        the `__init__.py`).
    """

    #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
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
    )

    #! List of allowed HTTP methods against a whole
    #! resource (eg /user); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_list_allowed_methods = None

    #! List of allowed HTTP methods against a single
    #! resource (eg /user/1); if undeclared or None, will be defaulted
    #! to `http_allowed_methods`.
    http_detail_allowed_methods = None

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

    #! Mapping of encoders known by this resource.
    encoders = {
        'json': 'armet.encoders.Json',
        'xml': 'armet.encoders.Xml',
        'text': 'armet.encoders.Text',
    }

    #! List of allowed encoders of the understood encoders.
    allowed_encoders = (
        'json',
        'xml',
        'text',
    )

    #! Name of the default encoder of the list of understood encoders.
    default_encoder = 'json'

    #! List of decoders known by this resource.
    decoders = {
        'form': 'armet.decoders.Form',
        'xml': 'armet.decoders.Xml',
    }

    #! List of allowed decoders of the understood decoders.
    allowed_decoders = (
        'form',
        'xml',
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

    #! The name of the resource URI attribute on the resource.
    #! Specify `None` to not have the URI be included.
    resource_uri = 'resource_uri'

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
    authorization = authorization.Resource({
        "create": ("add",),
        "update": ("change",),
        "delete": ("delete",),
        "read":   ("read",)
    })

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
    _url_base_regex = r'^{}{{}}/??(?:\.(?P<format>[^/]*?))?/?$'

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

            # Initiate the dispatch cycle and return its result
            return obj.dispatch()

        except exceptions.Error as ex:
            # Some known error was thrown before the dispatch cycle; dispatch.
            return ex.dispatch()

        except BaseException:
            # TODO: Notify system administrator of error

            # Log that an unknown exception occured to help those poor
            # system administrators.
            logger.exception('Internal server error.')

            # Return an empty body indicative of a server failure.
            return http.Response(status=http.client.INTERNAL_SERVER_ERROR)

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
        kwargs['parent'] = parent = helpers.parent(
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

    def dispatch(self):
        """
        Performs common work such as authentication, decoding, etc. before
        handing complete control of the result to a function with the
        same name as the request method.
        """
        try:
            # Parse query parameters
            self.query = query.Query(self.request.META['QUERY_STRING'])

            # Assert authentication and attempt to get a valid user object.
            self.authenticate()

            # Determine the HTTP method; function is now the method function
            # in this resource.
            function = self._determine_method()

            # Detect an appropriate encoder and store it in the resource
            # object for later use.
            self.encoder = self._determine_encoder()

            self.authorize_resource()

            data = None
            if self.request.body:
                # Determine an approparite decoder and decode the request body.
                data = self.decode(self.request.body)

                # Run clean cycle over decoded body
                data = self.clean(data)

                # TODO: Assert object-level authorization

            # Delegate to the determined function and return its response.
            return function(data)

        except exceptions.Error as ex:
            # Known error occured; encode it and return the response.
            return ex.dispatch(self.encoder)

    def authorize_resource(self):
        """Attempts to assert authorization for access to this resource.
        If unable to assert, it throws a forbidden.
        """
        if not self.authorization.is_accessible(
                self.request,
                self.request.method):
            raise exceptions.Forbidden()

    def authenticate(self):
        """Attempts to assert authentication."""
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

    def make_response(self, data, status):
        """Builds a response object from the data and status code."""
        response = http.Response(status=status)

        # Prepare the data for transmission.
        data = self.prepare(data)

        if data is not None:
            # Some kind of data was provided; encode and provide the
            # correct mimetype.
            response.content = self.encoder.encode(data)
            response['Content-Type'] = self.encoder.mimetype

        # Declare who we are in the header.
        response['Content-Location'] = self.url

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
        if relation is not None and len(self._attributes[name].path) <= 1:
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
                parent=helpers.parent(self.__class__(
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

    def prepare_resource_uri(self, obj, value):
        """Set the resource URI on the object."""
        try:
            # Reverse the url to make the `resource_uri`.
            return self.reverse(self.make_slug(obj), None,
                self.parent, self.local)

        except urlresolvers.NoReverseMatch:
            if not self.local:
                # Are we mis-used?
                raise ImproperlyConfigured(
                    'A non-publicly exposed resource must be '
                    'declared local.')

            # Nope; re-raise the proper error message.
            raise

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

            except (ValueError, AttributeError, TypeError) as ex:
                # Something weird happened with a path segment.
                raise exceptions.NotFound()

        # Return the resultant object.
        return obj

    def clean(self, data):
        """Cleans data from the request for processing."""
        # TODO: Resolve relation URIs (eg. /resource/:slug/).
        # TODO: Run micro-clean cycle using attribute-level cleaning in order to
        #       support things like fuzzy dates.

        if self.form is not None:
            # Instantiate form using provided data (if form exists).
            # form = self.form()
            pass

        return data

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

    @classmethod
    def reverse(cls, slug=None, path=None, parent=None, local=False):
        """Reverses a URL for the resource or for the passed object.

        @parent
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

                except TypeError:
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
        # Build and return the response object
        return self.make_response(None, http.client.NO_CONTENT)

    @property
    def _allowed_methods(self):
        """Retrieves a list of allowed HTTP methods for the current request."""
        return (self.http_detail_allowed_methods if self.slug is not None else
            self.http_list_allowed_methods)

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

            # Decode and return the request body
            return decoder.decode(self.request, self._attributes)

        # No content type header was presented; attempt to decode using
        # all available decoders.
        for decoder in six.itervalues(self.decoders):
            try:
                # Attemp to decode and return the body.
                return decoder.decode(self.request, self._attributes)

            except decoders.DecodingError:
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
        operations = self._allowed_operations
        if operation not in operations:
            # Operation not allowed in this context; build message
            # to display in the body.
            data = {}
            data['allowed'] = operations
            data['message'] = (
                'Operation not allowed on `{}`; '
                'see `allowed` for allowed operations.').format(operation)

            # Assert conditiion and bail.
            raise exceptions.Forbidden(data)
