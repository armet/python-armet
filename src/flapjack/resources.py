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


# class ResourceFactory(type):

#     # def __new__ .. ?

#     def __init__()

class Resource(object):

    #! Default list of allowed HTTP methods.
    http_allowed_methods = [
        'get',
        'post',
        'put',
        'delete',
        # TODO: 'patch',
        # ..
        # TODO: 'head',
        # <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.4>
        # TODO: 'options'
        # <http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.2>
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
    form = Form

    #! Authentication class to use when checking authentication.  Do not
    #! instantiate a class when doing this
    authentication = authn.Authentication

    #! Authorization class to use when checking authorization.  Do not
    #! instantiate a class when using this
    authorization = authz.Authorization

    def __init__(self):
        # Initialize name to be the name of the instantiated class if it was
        # not defined in the class definition.
        if self.name is None:
            self.name = self.__class__.__name__.lower()

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
            obj = None
            if request.body:
                # Request a decode and proceed to decode the request.
                obj = decoders.find(self.request)(self.request)

                # TODO: Run through form clean cycle
                # TODO: Authz check (w/object)

            # Delegate to an appropriate method to grab the response
            obj = function(obj, **kwargs)
            if obj is not None:
                # Run object through prepare cycle
                print(obj)
                obj = self.prepare(obj)
                print(obj)

                # Encode and return the object
                # TODO: Support returning other 2xx ..
                return self.encode(obj)
            else:
                # TODO: Support returning other 2xx ..
                return HttpResponse()

        except exceptions.Error as ex:
            return ex.response

        except BaseException as ex:
            if settings.DEBUG:
                # We're debugging; just re-raise the error
                raise

            # TODO: Log error and report to system admins.
            # Don't return a body; just notify server failure.
            return HttpResponse(status=500)

    def prepare(self, data):
        # ..
        try:
            print(iter(data))
            iter(data)
        except TypeError:
            # Not iterable
            pass
        else:
            # Iterable ..
            print('yo?')
            objs = []
            for item in data:
                obj = {}
                for name, field in self.form.fields.items():
                    obj[name] = getattr(item, name, None)
                objs.append(obj)
            return objs

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
        return patterns('',
            url(pattern.format(''), self.dispatch, name='dispatch'),
            url(pattern.format('/(?P<id>.*?)'), self.dispatch, name='dispatch')
        )


class Model(Resource):
    """Implementation of `Resource` for django's models.
    """
    #! The class object of the django model this resource is exposing.
    model = None

    def __init__(self):
        # TODO: Move this to the metaclass
        class Form(ModelForm):
            class Meta:
                model = self.model

        self.form = Form()

        super(Model, self).__init__()

    def read(self, **kwargs):
        # TODO: filtering
        return self.model.objects.all()
