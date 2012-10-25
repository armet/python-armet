""" ..
"""
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.forms import Form
from ..http import HttpResponse
from .. import encoders, exceptions, decoders
from .meta import Model as ModelMeta
from .meta import Resource as ResourceMeta
from .fields import Related
from collections import OrderedDict
# from . import authentication as authn
# from . import authorization as authz
from django.utils.functional import cached_property
import six


class Resource(six.with_metaclass(ResourceMeta)):

    #! Default list of allowed HTTP methods.
    http_allowed_methods = (
        'get',
        'post',
        'put',
        'delete',
        'patch',
    )

    #! The list of method names that we understand but do not neccesarily
    #! support.
    http_method_names = (
        'get',
        'post',
        'put',
        'delete',
        'patch',
        'options',
        'head',
        'connect',
        'trace',
    )

    #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
    name = None

    #! Dictionary of the relations for this resource mapping the names of the
    #! fields to the resources they relate to.
    relations = None

    #! Form to use to proxy the validation and clean cycles.
    form = Form

    #! Authentication class to use when checking authentication.
    # authentication = authn.Authentication

    #! Authorization class to use when checking authorization.
    # authorization = authz.Authorization

    @cached_property
    def _allowed_methods_header(cls):
        allow = [m.upper() for m in cls.http_allowed_methods]
        return ', '.join(allow).strip()

    def __init__(self):
        #! HTTP status of the entire cycle.
        self.status = 200

    def find_method(self):
        """Ensures method is acceptable."""
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

        if self.method not in self.http_allowed_methods:
            # Method understood but not allowed; die.
            response = HttpResponse()
            response['Allow'] = self._allowed_methods_header
            raise exceptions.MethodNotAllowed(response)

        function = getattr(self, self.method, None)
        if function is None:
            # Method understood and allowed but not implemented; die.
            raise exceptions.NotImplemented()

        # Method is understood, allowed and implemented; continue.
        return function

    def process(self,
                request,
                identifier=None,
                components=None,
                encoder=None
            ):

        # Set request on the instance to allow functions to have it
        # without lobbing it around
        self.request = request

        # TODO: Get rid of the need for this
        #self.encoder = encoder

        # Ensure the request method is present in the list of
        # allowed HTTP methods
        function = self.find_method()

        # Build auth classes and check initial auth
        # self.authn = self.authentication(request)
        # self.authz = self.authorization(request, method_name)

        # if not self.authn.is_authenticated:
        #     # not authenticated, panic
        #     # response =
        #     pass

        # By default, there is no object (for get and delete requests)
        request_obj = None
        if request.body:
            # Request a decode and proceed to decode the request.
            request_obj = decoders.find(self.request).decode(self.request)

            # Run through form clean cycle
            request_obj = self.clean(request_obj)

            # TODO: Authz check (w/obj)

        # Delegate to an appropriate method to grab the response;
        items = function(request_obj, identifier, **request.GET)

        if items is not None:
            # Run items through prepare cycle
            return self.prepare(items, components)

        # Nothing got from method; return nothing

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # ..
        try:
            # We start off with a successful response; let's see what happens..
            self.status = 200

            # We start off nowhere
            self.location = None

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            self.encoder = encoders.find(request, kwargs.get('format'))

            # Fire us off
            response_obj = self.process(
                    request,
                    identifier=kwargs.get('id'),
                    components=kwargs.get('components'),
                    #encoder=encoder
                )

            if response_obj is not None:
                # Encode and the object into a response
                response = self.encoder.encode(response_obj)
                response.status_code = self.status

                # Get current location
                response['Location'] = self.reverse(kwargs)

                # Do we have an alternative location ?
                if self.location is not None:
                    response['Content-Location'] = self.location

                # Return the constructed response
                return response
            else:
                # We have no body; just return.
                return HttpResponse(status=self.status)

        except exceptions.Error as ex:
            return ex.response

        except BaseException as ex:
            if settings.DEBUG:
                # We're debugging; just re-raise the error
                raise

            # TODO: Log error and report to system admins.
            # Don't return a body; just notify server failure.
            return HttpResponse(status=500)

    @classmethod
    def reverse(cls, item=None):
        kwargs = {'resource': cls.name}
        if item is not None:
            try:
                # Attempt to get the identifier off of the item
                # by treating it as a dictionary
                if 'id' in item:
                    kwargs['id'] = item['id']

                if 'components' in item:
                    kwargs['components'] = item['components']
            except:
                try:
                    # That failed; let's try direct access -- maybe we have
                    # an object
                    kwargs['id'] = item.id
                except:
                    # We're done, it must be an id
                    kwargs['id'] = item
        return reverse('api_dispatch', kwargs=kwargs)

    @staticmethod
    def resolve(path):
        try:
            # Attempt to resolve the path
            resolution = resolve(path)
        except:
            # Assume we're already resolved
            return path

        try:
            return resolution.func.__self__.read(resolution.kwargs['id']).id
        except:
            # Return the id; its not valid -- let the form tell us so
            return resolution.kwargs['id']

    def _prepare_related(self, item, relation):
         # This is a related field; transform the object to to its uri
        try:
            # Attempt to resolve the relation if it can be
            item = item()
        except:
            # It can't be; oh well
            pass

        try:
            # Iterate and reverse each relation
            item = [relation.reverse(x) for x in item]

        except TypeError:
            # Not iterable; reverse just the one
            item = relation.reverse(item)

        # Return our new-fangled list
        return item

    def _prepare_item(self, item):
        obj = OrderedDict()

        # Append the URI
        # TODO: Need some configuration so the name can be changed
        obj['.'] = self.reverse(item)

        for name, field in self._fields.items():
            # Constuct object containing all properties
            # from the item
            obj[name] = getattr(item, name, None)

            # Run it through the (optional) prepare_FOO function
            prepare_foo = getattr(self, 'prepare_{}'.format(name), None)
            if prepare_foo is not None:
                obj[name] = prepare_foo(obj[name])

            if isinstance(field, Related) and obj[name] is not None:
                obj[name] = self._prepare_related(obj[name], field.relation)

            if field.collection:
                # Ensure we always have a collection on collection fields
                if obj[name] is None:
                    obj[name] = []
                elif isinstance(obj[name], basestring):
                    obj[name] = obj[name],
                else:
                    try:
                        iter(obj[name])
                    except TypeError:
                        obj[name] = obj[name],

        # Return the constructed object
        return obj

    def prepare(self, items, components=None):
        try:
            # Attempt to iterate and prepare each item
            response = []
            for item in items:
                obj = self._prepare_item(item)
                response.append(obj)
            return response
        except TypeError:
            # Not iterable; we only have one
            response = self._prepare_item(items)

        # Are we accessing a sub-resource on this item ?
        if components:
            # Parse the component list
            components = components.split('/')
            name = components[0]

            if name not in self._fields:
                # Field not found; die
                raise exceptions.NotFound()

            # Grab the field in question
            field = self._fields[name]

            if isinstance(field, Related):
                if not field.collection:
                    # Damn; related field; send it back through
                    resolution = resolve(response[name])
                    response = resolution.func.__self__.process(
                        request=self.request,
                        identifier=resolution.kwargs['id'],
                        components='/'.join(components[1:]))
                        #encoder=self.encoder)

            elif not field.collection:
                # Yes; simple sub-resource access
                response = response[name]

        # Pass it along
        return response

    def clean(self, obj):
        # Before the object goes anywhere its relations need to be resolved.
        for field in self._fields.values():
            if field.name in obj:
                if isinstance(field, Related):
                    value = obj[field.name]
                    if field.collection:
                        value = [field.relation.resolve(x) for x in value]
                    else:
                        value = field.relation.resolve(value)
                    obj[field.name] = value

        # Create form to proxy validation
        form = self.form(data=obj)

        # Attempt to validate the form
        if not form.is_valid():
            # We got invalid data; tsk.. tsk..; throw a bad request
            raise exceptions.BadRequest(self.encoder.encode(form.errors))

        # We should have good, sanitized data now (thank you, forms)
        return form.cleaned_data

    def read(self, identifier=None, **kwargs):
        raise exceptions.NotImplemented()

    def create(self, obj):
        raise exceptions.NotImplemented()

    def destroy(self, identifier):
        raise exceptions.NotImplemented()

    def get(self, obj=None, identifier=None, **kwargs):
        # Delegate to `read` to actually grab a list of items.
        return self.read(identifier, **kwargs)

    def post(self, obj, identifier=None, **kwargs):
        if identifier is None:
            # Delegate to `create` to actually create a new item.
            # TODO: Where should the configuration option go for
            #   returning no body v/s returning a body?
            self.status = 201
            return self.create(obj)

        else:
            # Attempting to create a sub-resource.
            raise exceptions.NotImplemented()

    # def put(self, obj, identifier=None, *args, **kwargs):
    #     if identifier is None:
    #         # Attempting to overwrite everything

    def delete(self, obj, identifier=None, *args, **kwargs):
        if identifier is None:
            # Attempting to delete everything.
            raise exceptions.NotImplemented()

        else:
            # Delegate to `destroy` to actually delete the item.
            self.status = 204
            self.destroy(identifier)

    def url(self, regex=''):
        format = r'(?:\.(?P<format>[^/]*?))?'
        pattern = r'^{}{{}}/??{}/?$'.format(self.name, format)
        return url(pattern.format(regex),
                self.dispatch,
                name='api_dispatch',
                kwargs={
                    'resource': self.name
                }
            )

    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to."""
        identifier = r'/(?P<id>[^/]*?)'
        return patterns('',
                self.url(),
                self.url(identifier),
                self.url(r'{}/(?P<components>.*?)'.format(identifier)),
            )


class Model(six.with_metaclass(ModelMeta, Resource)):
    """Implementation of `Resource` for django's models.
    """

    #! The class object of the django model this resource is exposing.
    model = None

    def _prepare_related(self, item, relation):
        try:
            # First attempt to resolve the item as queryset
            item = item.all()
        except:
            # No dice; move along
            pass

        # Finish us up
        return super(Model, self)._prepare_related(item, relation)

    def read(self, identifier=None, **kwargs):
        # TODO: filtering
        if identifier is not None:
            try:
                return self.model.objects.get(pk=identifier)
            except:
                raise exceptions.NotFound()
        else:
            return self.model.objects.all()

    def create(self, obj):
        # Iterate through and set all fields that we can initially
        params = {}
        for field in self._fields.values():
            if field.name not in obj:
                # Isn't here; move along
                continue

            if isinstance(field, Related) and field.collection:
                # This is a m2m field; move along for now
                continue

            # This is not a m2m field; we can set this now
            params[field.name] = obj[field.name]

        # Perform the initial create
        model = self.model.objects.create(**params)

        # Iterate through again and set the m2m bits
        for field in self._fields.values():
            if field.name not in obj:
                # Isn't here; move along
                continue

            if isinstance(field, Related) and field.collection:
                # This is a m2m field; we can set this now
                setattr(model, field.name, obj[field.name])

        # Perform a final save
        model.save()

        # Return the fully constructed model
        return model

    def update(self):
        pass

    def destroy(self, identifier):
        # Delegate to django to perform the creation
        self.model.objects.get(pk=identifier).delete()
