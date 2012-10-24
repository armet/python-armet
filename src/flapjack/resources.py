""" ..
"""
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.utils.functional import cached_property
from django.conf import settings
from django.forms import Form, ModelForm
from .http import HttpResponse
from . import encoders, exceptions, decoders
from . import authentication as authn
from . import authorization as authz
import six


class Field(object):
    # ..
    def __init__(self, name, **kwargs):
        #! Name of the field on the object instance.
        self.name = name

        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)


class DeclarativeResource(type):

    def _is_visible(cls, name):
        if cls.form._meta.fields is not None:
            if name not in cls.form._meta.fields:
                # There is a whitelist present on the bound form; this field
                # is not declared in it.
                return False

        if cls.form._meta.exclude is not None:
            if name in cls.form._meta.exclude:
                # There is a blacklist present on the bound form; this field
                # is declared in it.
                return False

        # Field is good and visible -- as far as we can see here.
        return True

    def __init__(cls, name, bases, attributes):
        # Ensure we have a valid name property.
        if 'name' not in attributes:
            # Default to the lowercased name of the class
            cls.name = name.lower()

        # Initialize listing of fields
        cls._fields = {}

        # Generate the list of fields using the provided form
        if hasattr(getattr(cls, 'form', None), 'declared_fields'):
            # Iterate through each declared field on the form
            for name, field in cls.form.declared_fields.items():
                if cls._is_visible(name):
                    # Field has been declared visible; construct it
                    # and add it to our list
                    cls._fields[name] = Field(name, **field.__dict__)

        # Delegate to python magic to initialize the class object
        super(DeclarativeResource, cls).__init__(name, bases, attributes)


class Resource(six.with_metaclass(DeclarativeResource)):

    #! Default list of allowed HTTP methods.
    http_allowed_methods = (
        'get',
        'post',
        'put',
        'delete',
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

    #! Form to use to proxy the validation and clean cycles.
    form = Form

    #! Authentication class to use when checking authentication.
    authentication = authn.Authentication

    #! Authorization class to use when checking authorization.
    authorization = authz.Authorization

    def __init__(self):
        #! HTTP status of the entire cycle.
        self.status = 200

    @cached_property
    def _allowed_methods_header(self):
        allow = [m.upper() for m in self.http_allowed_methods]
        return ', '.join(allow).strip()

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

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # ..
        try:
            # Set request on the instance to allow functions to have it
            # without lobbing it around
            self.request = request

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

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            self.encoder = encoders.find(self.request, kwargs.get('format'))

            # By default, there is no object (for get and delete requests)
            request_obj = None
            if request.body:
                # Request a decode and proceed to decode the request.
                request_obj = decoders.find(self.request).decode(self.request)

                # TODO: Run through form clean cycle
                # TODO: Authz check (w/obj)

            # Delegate to an appropriate method to grab the response;
            items = function(request_obj, kwargs.get('id'), **request.GET)
            if items is not None:
                # Run items through prepare cycle
                response_obj = self.prepare(items)

                # Encode and return the object
                response = self.encoder.encode(response_obj)
                response.status_code = self.status
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

    def _prepare_item(self, item):
        obj = {}
        for name, field in self._fields.items():
            # Constuct object containing all properties
            # from the item
            obj[name] = getattr(item, name, None)

            # Run it through the (optional) prepare_FOO function
            prepare_foo = getattr(self, 'prepare_{}'.format(name), None)
            if prepare_foo is not None:
                obj[name] = prepare_foo(obj[name])

        return obj

    def prepare(self, items):
        try:
            # Attempt to iterate and prepare each item
            return [self._prepare_item(x) for x in items]
        except TypeError:
            # Not iterable; we only have one
            return self._prepare_item(items)

    def read(self, identifier=None, **kwargs):
        raise exceptions.NotImplemented()

    def get(self, obj=None, identifier=None, **kwargs):
        # Delegate to `read` to actually grab a list of items.
        return self.read(identifier, **kwargs)

    def post(self, obj, identifier=None, **kwargs):
        raise exceptions.NotImplemented()

    def put(self, obj, identifier=None, *args, **kwargs):
        raise exceptions.NotImplemented()

    def delete(self, obj, identifier=None, *args, **kwargs):
        raise exceptions.NotImplemented()

    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to."""
        #! In order to undo a reverse() call (to get the resource from a slug),
        #! call django.core.urlresolvers.resolve(slug).  the resulting object's
        #! func attribute is the entrypoint into the resource.  So, to get the
        #! resource object, simply
        #! django.core.urlresolvers.resolve(slug).func.__self__
        pattern = '^{}{{}}/??(?:\.(?P<format>[^/]*?))?/?$'.format(self.name)
        name = 'api:dispatch'
        kwargs = {'resource': self.name}
        return patterns('',
            # The resource as a whole.
            url(pattern.format(''),
                self.dispatch,
                name=name,
                kwargs=kwargs
            ),

            # Individual item of this resource.
            url(
                pattern.format('/(?P<id>.*?)'),
                self.dispatch,
                name=name,
                kwargs=kwargs
            )
        )


class DeclarativeModel(DeclarativeResource):

    def __init__(cls, name, bases, attributes):
        # Delegate to more magic to initialize the class object
        super(DeclarativeModel, cls).__init__(name, bases, attributes)

        # Ensure we have a valid model form instance to use to generate
        # field references
        model = getattr(cls, 'model', None)
        if model is not None:
            if not issubclass(getattr(cls, 'form', None), ModelForm):
                # Construct a form class that is bound to our model
                class Form(ModelForm):
                    class Meta:
                        model = model

                # Declare our use of the form class
                cls.form = Form

            # Iterate through each declared field on the model
            for field in cls.model._meta.local_fields:
                if cls._is_visible(field.name):
                    if field.name not in cls._fields:
                        # Field is visible and not already declared explicitly
                        # by the model; add it to our list
                        cls._fields[field.name] = Field(field.name)


class Model(six.with_metaclass(DeclarativeModel, Resource)):
    """Implementation of `Resource` for django's models.
    """
    #! The class object of the django model this resource is exposing.
    model = None

    def read(self, identifier=None, **kwargs):
        # TODO: filtering
        if identifier is not None:
            return self.model.objects.get(pk=identifier)
        else:
            return self.model.objects.all()
