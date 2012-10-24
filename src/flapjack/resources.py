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


class DeclarativeResource(type):

    def __init__(cls, name, bases, dct):
        # Ensure we have a valid name property.
        if 'name' not in dct:
            # Default to the lowercased name of the class
            cls.name = name.lower()

        # Delegate to python magic to initialize the class object
        super(DeclarativeResource, cls).__init__(name, bases, dct)


class Resource(six.with_metaclass(DeclarativeResource)):

    #! Default list of allowed HTTP methods.
    http_allowed_methods = [
        'get',
        'post',
        'put',
        'delete'
    ]

    #! The list of method names that we understand but do not neccesarily
    #! support
    http_method_names = [
        'get',
        'post',
        'put',
        'delete',
        'patch',
        'options',
        'head',
        'connect',
        'trace',
    ]

    #! Name of the resource to use in URIs; defaults to `__name__.lower()`.
    name = None

    #! Form to use to proxy the validation and clean cycles.
    form_class = Form

    #! Authentication class to use when checking authentication.  Do not
    #! instantiate a class when doing this
    authentication = authn.Authentication

    #! Authorization class to use when checking authorization.  Do not
    #! instantiate a class when using this
    authorization = authz.Authorization

    def __init__(self):
        #! HTTP status of the entire cycle.
        self.status = 200

        #! Form object to use for the cycle (when we have content).
        self.form = None

    @cached_property
    def fields(self):
        """Fields iterable to use for the preparation cycle."""
        return self.form_class().fields

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
            self.encode = encoders.find(self.request, **kwargs)

            # By default, there is no object (for get and delete requests)
            request_obj = None
            if request.body:
                # Request a decode and proceed to decode the request.
                request_obj = decoders.find(self.request)(self.request)

                # TODO: Run through form clean cycle
                # TODO: Authz check (w/obj)

            # Delegate to an appropriate method to grab the response;
            items = function(request_obj, **kwargs)
            if items is not None:
                # Run items through prepare cycle
                response_obj = self.prepare(items)

                # Encode and return the object
                response = self.encode(response_obj)
                response.status_code = self.status
                return response
            else:
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
        for name, field in self.fields.items():
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

    def read(self, **kwargs):
        raise exceptions.NotImplemented()

    def get(self, obj=None, **kwargs):
        # TODO: caching, pagination
        # Delegate to `read` to actually grab a list of items
        items = self.read(**kwargs)

        # encode the list of read items.
        return items

    def post(self, obj, **kwargs):
        raise exceptions.NotImplemented()

    def put(self, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    def delete(self, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to.
        """
        pattern = '^{}{{}}(?:\.(?P<format>[^/]*?))?/?$'.format(self.name)
        name = 'api_dispatch'
        kwargs = {'resource': self.name}
        print self.name
        return patterns('',
            url(pattern.format(''), self.dispatch, name=name, kwargs=kwargs),
            url(
                pattern.format('/(?P<id>.*?)'),
                self.dispatch,
                name=name,
                kwargs=kwargs)
        )


class DeclarativeModel(DeclarativeResource):

    def __init__(cls, name, bases, dct):
        # Delegate to more magic to initialize the class object
        super(DeclarativeModel, cls).__init__(name, bases, dct)

        # Ensure we have a valid model form instance to use to generate
        # field references
        model_class = getattr(cls, 'model_class', None)
        if model_class is not None and \
                not isinstance(getattr(cls, 'form_class', None), ModelForm):
            class Form(ModelForm):
                class Meta:
                    model = model_class

            cls.form_class = Form


class Model(six.with_metaclass(DeclarativeModel, Resource)):
    """Implementation of `Resource` for django's models.
    """
    #! The class object of the django model this resource is exposing.
    model_class = None

    def read(self, **kwargs):
        # TODO: filtering
        return self.model_class.objects.all()
