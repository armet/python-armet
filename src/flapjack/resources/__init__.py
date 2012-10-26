# coding=utf-8
""" ..
"""
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.forms import Form
from ..http import HttpResponse, constants
from .. import encoders, exceptions, decoders
from .meta import Model, Resource
from collections import OrderedDict
# from . import authentication as authn
# from . import authorization as authz
from django.utils.functional import cached_property
import six
from .. import utils


class Resource(six.with_metaclass(Resource)):

    #! List of allowed HTTP methods (in general).
    http_allowed_methods = (
        'get',
        'post',
        'put',
        'delete',
        'patch'
    )

    #! List of allowed HTTP methods (on accessing the whole resource).
    http_list_allowed_methods = None

    #! List of allowed HTTP methods (on accessing a specific resource).
    http_detail_allowed_methods = None

    #! List of method names that we understand but do not neccesarily support.
    http_method_names = (
        'get',
        'post',
        'put',
        'delete',
        'patch'
        'options',
        'head',
        'connect',
        'trace',
    )

    #! List of allowed resource operations.
    allowed_methods = (
        'read',
        'create',
        'update',
        'destroy',
    )

    #! List of allowed resource operations (on accessing the whole resource).
    list_allowed_methods = None

    #! List of allowed resource operations (on accessing a specific resource).
    detail_allowed_methods = None

    #! Name of the django application; used for namespacing.
    #! Defaults to the actual application label -- no need to set this unless
    #! you want to be strange.
    app_label = None

    #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
    name = None

    #! Dictionary of the relations for this resource; maps the names of the
    #! fields to the resources they relate to. The key is the name of the
    #! field on the resource; the value is either the resource class object or
    #! a string formatted as '{app_label}.{resource_name}'.
    #!
    #! @example
    #!   relations = {
    #!           # Many-to-many field
    #!           'apples': Apple,
    #!
    #!          # Foreign key field (notice there is no difference)
    #!          'banana': Banana,
    #!
    #!          # Notice django-style app + resource name
    #!          'orange': 'fruit.Orange'
    #!      }
    relations = None

    #! Iterable of the fields on this resource that may be filtered using
    #! query parameters.
    filterable = None

    #! Class object of the filter class to proxy filtering to for filtering
    #! filterables.
    filterer = None

    #! Form class to use to provide the validation and sanitization cycle.
    form = None

    #! Authentication class to proxy authentication requests to; leave
    #! unspecified for no authentication.
    authentication = None

    #! Authorization class to proxy authorization requests to; leave
    #! unspecified for no authorization.
    authorization = None

    #! Name of the field on the response object that contains the resource URI.
    #! Specify `None` to not include, use, or generate one.
    resource_uri = 'resource_uri'

    #! Default encoder to use if there is no accept header or the accept
    #! header specified something akin to '*/*'.
    default_encoder = encoders.Json

    #! Specifies that POST should return data; defaults to False.
    http_post_return_data = False

    #! Specifies that PUT should return data; defaults to False.
    http_put_return_data = False

    #! Name of the URL that is used in the url configuration.
    url_name = "api_dispatch"

    @classmethod
    @csrf_exempt
    def view(cls, request, *args, **kwargs):
        try:
            # Instantiate the resource to use for the cycle
            resource = cls(request,
                kwargs.get('id'),
                kwargs.get('components'))

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            encoder = None
            encoder = encoders.find(request, kwargs.get('format'))

            # Initiate the dispatch and return the response
            content = resource.dispatch()

            # Encode the content (if any) and return the response
            response = encoder.encode(content) if content else HttpResponse()
            response.status_code = resource.status
            # TODO: response['Location'] (self.reverse(kwargs)) ?
            # TODO: response['Content-Location'] (self.location) ?
            return response

        except exceptions.Error as ex:
            # Something went wrong; deal with it and return the response
            return ex.encode(encoder or cls.default_encoder)

        except BaseException as ex:
            if settings.DEBUG:
                # We're debugging; just re-raise the error
                raise

            # TODO: Log error and report to system admins.
            # Don't return a body; just notify server failure.
            return HttpResponse(status=500)

    @classmethod
    def url(cls, match=''):
        pattern = r'^{}{{}}/??(?:\.(?P<format>[^/]*?))?/?$'.format(cls.name)
        return url(
                pattern.format(match),
                cls.view,
                name=cls.url_name,
                kwargs={'resource': cls.name}
            )

    @utils.classproperty
    def urls(cls):
        identifier = r'/(?P<id>[^/]*?)'
        return patterns('',
                cls.url(),
                cls.url(identifier),
                cls.url(r'{}/(?P<components>.*?)'.format(identifier)),
            )

    def __init__(self, request, format=None, identifier=None, components=None):
        """Initialize ourself and prepare for the dispatch process."""
        #! Status of the request cycle.
        self.status = constants.OK

        #! Django request object.
        self.request = request

        #! Shorthand format name if provided.
        self.format = format

        #! Identifier indicating we are accessing an individual resource.
        self.identifier = identifier

        #! Components list that is for sub resource resolution.
        self.components = components or None

        #! Encoder to use to encode response objects with.
        self.encoder = None

    def dispatch(self):
        # Determine the method; returns our function to delegate to
        function = self.determine_method()

        # Grab the request object if we can
        obj = None
        if self.request.body:
            # Request a decoder and decode away
            obj = decoders.find(self.request).decode(self.request)

            # Run the object through a clean cycle
            obj = self.clean(obj)

        return obj

        # # Execute the function found earlier
        # response = function(obj)

        # # If we got anything back ..
        # if response is not None:
        #     # Run it through a preparation cycle
        #     return self.prepare(response)

        # Didn't get anything back; return nothing

    @property
    def http_allowed_methods_header(self):
        allow = (m.upper() for m in self.get_http_allowed_methods())
        return ', '.join(allow).strip()

    def get_http_allowed_methods(self):
        """Gets list of allowed HTTP methods for the current request."""
        if self.identifier is not None:
            return self.http_detail_allowed_methods
        else:
            return self.http_list_allowed_methods

    def is_http_method_allowed(self, method):
        """Checks if the passed is an allowed HTTP method."""
        return method in self.get_http_allowed_methods()

    def determine_method(self):
        """Ensures HTTP method is acceptable."""
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in self.request.META:
            # Someone is using a client that isn't smart enough
            # to send proper verbs
            self.method = self.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']

        else:
            # Normal client; behave normally
            self.method = self.request.method.lower()

        if self.method not in self.http_method_names:
            # Method not understood by our library; die.
            raise exceptions.NotImplemented()

        if not self.is_http_method_allowed(self.method):
            # Method understood but not allowed; die.
            raise exceptions.MethodNotAllowed(self.http_allowed_methods_header)

        function = getattr(self, self.method, None)
        if function is None:
            # Method understood and allowed but not implemented; die.
            raise exceptions.NotImplemented()

        # Method is understood, allowed and implemented; continue.
        return function

    def relation_clean(self, field, values):
        if not isinstance(values, basestring):
            try:
                # Need to resolve all the values
                return [field.relation.resolve(value) for value in values]
            except TypeError:
                pass

        # Nope; should just be one that gets resolved
        return field.relation.resolve(values)

    def clean(self, obj):
        # Before the object goes anywhere its relations need to be resolved.
        for name, field in self.fields.items():
            if name in obj and field.relation is not None:
                obj[name] = self.relation_clean(field, obj[name])

        # Create a form instance to proxy validation
        form = self.form(data=obj)

        # Attempt to validate the form
        if not form.is_valid():
            # We got invalid data; tsk.. tsk..; throw a bad request
            raise exceptions.BadRequest(form.errors)

        # We should have good, sanitized data now (thank you, forms)
        return form.cleaned_data

    @staticmethod
    def resolve(path):
        try:
            # Attempt to resolve the path normally
            resolution = resolve(path)
        except:
            # Assume we're already resolved
            return path

        # ..

        # try:
        #     # Attempt to resolve the path
        #     resolution = resolve(path)
        # except:
        #     # Assume we're already resolved
        #     return path

        # try:
        #     return resolution.func.__self__.read(resolution.kwargs['id']).id
        # except:
        #     # Return the id; its not valid -- let the form tell us so
        #     return resolution.kwargs['id']

    def prepare(self, obj):
        pass

    def get(self, obj=None):
        # Delegate to `read` to actually grab a list of items.
        # return self.read(identifier, **kwargs)
        raise exceptions.NotImplemented()

    def post(self, obj=None):
        raise exceptions.NotImplemented()

    def put(self, obj=None):
        raise exceptions.NotImplemented()

    def delete(self, obj=None):
        raise exceptions.NotImplemented()


class Model(six.with_metaclass(Model, Resource)):

    #! Model class object to use to bind to this resource.
    #! Is overridden by the model option in the ModelForm form if specified.
    model = None

    @utils.classproperty
    @utils.memoize
    def queryset(cls):
        """Queryset that is used to read and filter data."""
        return cls.model.objects.all

#     @classmethod
#     def reverse(cls, item=None):
#         kwargs = {'resource': cls.name}
#         if item is not None:
#             try:
#                 # Attempt to get the identifier off of the item
#                 # by treating it as a dictionary
#                 if 'id' in item:
#                     kwargs['id'] = item['id']

#                 if 'components' in item:
#                     kwargs['components'] = item['components']
#             except:
#                 try:
#                     # That failed; let's try direct access -- maybe we have
#                     # an object
#                     kwargs['id'] = item.id
#                 except:
#                     # We're done, it must be an id
#                     kwargs['id'] = item
#         return reverse('api_dispatch', kwargs=kwargs)

#     @staticmethod
#     def resolve(path):
#         try:
#             # Attempt to resolve the path
#             resolution = resolve(path)
#         except:
#             # Assume we're already resolved
#             return path

#         try:
#             return resolution.func.__self__.read(resolution.kwargs['id']).id
#         except:
#             # Return the id; its not valid -- let the form tell us so
#             return resolution.kwargs['id']

#     def _prepare_related(self, item, relation):
#          # This is a related field; transform the object to to its uri
#         try:
#             # Attempt to resolve the relation if it can be
#             item = item()
#         except:
#             # It can't be; oh well
#             pass

#         try:
#             # Iterate and reverse each relation
#             item = [relation.reverse(x) for x in item]

#         except TypeError:
#             # Not iterable; reverse just the one
#             item = relation.reverse(item)

#         # Return our new-fangled list
#         return item

#     def _prepare_item(self, item):
#         obj = OrderedDict()

#         # Append the URI
#         # TODO: Need some configuration so the name can be changed
#         obj['.'] = self.reverse(item)

#         for name, field in self._fields.items():
#             # Constuct object containing all properties
#             # from the item
#             obj[name] = getattr(item, name, None)

#             # Run it through the (optional) prepare_FOO function
#             prepare_foo = getattr(self, 'prepare_{}'.format(name), None)
#             if prepare_foo is not None:
#                 obj[name] = prepare_foo(obj[name])

#             if field.relation is not None and obj[name] is not None:
#                 obj[name] = self._prepare_related(obj[name], field.relation)

#             if field.collection:
#                 # Ensure we always have a collection on collection fields
#                 if obj[name] is None:
#                     obj[name] = []
#                 elif isinstance(obj[name], basestring):
#                     obj[name] = obj[name],
#                 else:
#                     try:
#                         iter(obj[name])
#                     except TypeError:
#                         obj[name] = obj[name],

#         # Return the constructed object
#         return obj

#     def prepare(self, items, components=None):
#         try:
#             # Attempt to iterate and prepare each item
#             response = []
#             for item in items:
#                 obj = self._prepare_item(item)
#                 response.append(obj)
#             return response
#         except TypeError:
#             # Not iterable; we only have one
#             response = self._prepare_item(items)

#         # Are we accessing a sub-resource on this item ?
#         if components:
#             # Parse the component list
#             components = components.split('/')
#             name = components[0]

#             if name not in self._fields:
#                 # Field not found; die
#                 raise exceptions.NotFound()

#             # Grab the field in question
#             field = self._fields[name]

#             if field.relation is not None:
#                 if not field.collection:
#                     # Damn; related field; send it back through
#                     resolution = resolve(response[name])
#                     response = resolution.func.__self__.process(
#                         request=self.request,
#                         identifier=resolution.kwargs['id'],
#                         components='/'.join(components[1:]))
#                         #encoder=self.encoder)

#             elif not field.collection:
#                 # Yes; simple sub-resource access
#                 response = response[name]

#         # Pass it along
#         return response

#     def clean(self, obj):
#         # Before the object goes anywhere its relations need to be resolved.
#         for field in self._fields.values():
#             if field.name in obj:
#                 if field.relation is not None:
#                     value = obj[field.name]
#                     if field.collection:
#                         value = [field.relation.resolve(x) for x in value]
#                     else:
#                         value = field.relation.resolve(value)
#                     obj[field.name] = value

#         # Create form to proxy validation
#         form = self.form(data=obj)

#         # Attempt to validate the form
#         if not form.is_valid():
#             # We got invalid data; tsk.. tsk..; throw a bad request
#             raise exceptions.BadRequest(self.encoder.encode(form.errors))

#         # We should have good, sanitized data now (thank you, forms)
#         return form.cleaned_data

#     def read(self, identifier=None, **kwargs):
#         raise exceptions.NotImplemented()

#     def create(self, obj):
#         raise exceptions.NotImplemented()

#     def destroy(self, identifier):
#         raise exceptions.NotImplemented()

#     def get(self, obj=None, identifier=None, **kwargs):
#         # Delegate to `read` to actually grab a list of items.
#         return self.read(identifier, **kwargs)

#     def post(self, obj, identifier=None, **kwargs):
#         if identifier is None:
#             # Delegate to `create` to actually create a new item.
#             # TODO: Where should the configuration option go for
#             #   returning no body v/s returning a body?
#             self.status = 201
#             return self.create(obj)

#         else:
#             # Attempting to create a sub-resource.
#             raise exceptions.NotImplemented()

#     def put(self, obj, identifier=None, *args, **kwargs):
#         if identifier is None:
#             # Attempting to overwrite everything in the list..
#             # Yeah; not implemented (perhaps later)
#             raise exceptions.NotImplemented()

#     def delete(self, obj, identifier=None, *args, **kwargs):
#         if identifier is None:
#             # Attempting to delete everything.
#             raise exceptions.NotImplemented()

#         else:
#             # Delegate to `destroy` to actually delete the item.
#             self.status = 204
#             self.destroy(identifier)

#     def url(self, regex=''):
#         """Constructs a single URL by wrapping django's `url` method."""
#         format = r'(?:\.(?P<format>[^/]*?))?'
#         pattern = r'^{}{{}}/??{}/?$'.format(self.name, format)
#         return url(pattern.format(regex),
#                 self.dispatch,
#                 name='api_dispatch',
#                 kwargs={
#                     'resource': self.name
#                 }
#             )

#     @cached_property
#     def urls(self):
#         """Constructs the URLs that this resource will respond to."""
#         identifier = r'/(?P<id>[^/]*?)'
#         return patterns('',
#                 self.url(),
#                 self.url(identifier),
#                 self.url(r'{}/(?P<components>.*?)'.format(identifier)),
#             )


# class Model(six.with_metaclass(ModelMeta, Resource)):
#     """Implementation of `Resource` for django's models.
#     """

#     #! The class object of the django model this resource is exposing.
#     model = None

#     def _prepare_related(self, item, relation):
#         try:
#             # First attempt to resolve the item as queryset
#             item = item.all()
#         except:
#             # No dice; move along
#             pass

#         # Finish us up
#         return super(Model, self)._prepare_related(item, relation)

#     def read(self, identifier=None, **kwargs):
#         # TODO: filtering
#         if identifier is not None:
#             try:
#                 return self.model.objects.get(pk=identifier)
#             except:
#                 raise exceptions.NotFound()
#         else:
#             return self.model.objects.all()

#     def create(self, obj):
#         # Iterate through and set all fields that we can initially
#         params = {}
#         for field in self._fields.values():
#             if field.name not in obj:
#                 # Isn't here; move along
#                 continue

#             if field.relation is not None and field.collection:
#                 # This is a m2m field; move along for now
#                 continue

#             # This is not a m2m field; we can set this now
#             params[field.name] = obj[field.name]

#         # Perform the initial create
#         model = self.model.objects.create(**params)

#         # Iterate through again and set the m2m bits
#         for field in self._fields.values():
#             if field.name not in obj:
#                 # Isn't here; move along
#                 continue

#             if field.relation is not None and field.collection:
#                 # This is a m2m field; we can set this now
#                 setattr(model, field.name, obj[field.name])

#         # Perform a final save
#         model.save()

#         # Return the fully constructed model
#         return model

#     def update(self):
#         pass

#     def destroy(self, identifier):
#         # Delegate to django to perform the creation
#         self.model.objects.get(pk=identifier).delete()
