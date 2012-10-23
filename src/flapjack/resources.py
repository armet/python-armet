""" ..
"""
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.utils.functional import cached_property
from django.conf import settings
from . import encoders, exceptions, decoders
from . import authentication as authn
from . import authorization as authz


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

    def encode(self, obj=None, status=200):
        """Transforms python objects to an acceptable format for tansmission.
        """
        response = HttpResponse(status=status)
        if obj is not None:
            response.content = self.encoder.encode(obj)
            response['Content-Type'] = self.encoder.get_mimetype()
        else:
            # No need to specify the default content-type if we don't
            # have a body.
            del response['Content-Type']
        return response

    def decode(self, request):
        """Transforms recieved data to valid python objects.
        """
        # TODO: anything else to do here ?
        return self.decoder.decode(request)

    # TODO: add some magic to make this a class method
    @cached_property
    def allow_header(self):
        allow = [m.upper() for m in self.http_allowed_methods]
        return ', '.join(allow).strip()

    def find_method(self, request):
        """Ensures method is acceptable; throws appropriate exception elsewise.
        """
        if 'HTTP_X_HTTP_METHOD_OVERRIDE' in request.META:
            # Someone is using a client that isn't smart enough
            # to send proper verbs
            method_name = request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
        else:
            # Normal client; behave normally
            method_name = request.method.lower()

        if method_name not in self.http_method_names:
            # Method not understood by our library.  Die.
            response = HttpResponse()
            raise exceptions.NotImplemented(response)

        method = getattr(self, method_name, None)
        if method_name not in self.http_allowed_methods or method is None:
            # Method understood but not allowed.  Die.
            response = HttpResponse()
            response['Allow'] = self.allow_header
            raise exceptions.MethodNotAllowed(response)

        # Method is allowed, continue.
        return method, method_name

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # ..
        try:
            # Ensure the request method is present in the list of
            # allowed HTTP methods
            method, method_name = self.find_method(request)

            # Build auth classes and check initial auth
            self.authn = self.authentication(request)
            self.authz = self.authorization(request, method_name)

            if not self.authn.is_authenticated:
                # not authenticated, panic
                # response =
                pass

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            self.encoder = encoders.find_encoder(request, **kwargs)

            # TODO: Authn check
            # TODO: Authz check

            # By default, there is no object (for get and delete requests)
            obj = None
            if request.body:
                # Request a decode and proceed to decode the request.
                self.decoder = decoders.find_decoder(request)
                obj = self.decode(request)

                # TODO: Authz check (w/object)

            # Delegate to an appropriate method
            return method(request, obj, **kwargs)

        except exceptions.Error as ex:
            # TODO: We need to encode the error response.
            return ex.response

        except BaseException as ex:
            if settings.DEBUG:
                # We're debugging; just re-raise the error
                raise

            # Return no body
            # TODO: `del response['Content-Type']` needs to generalized
            #       somewhere; its everywhere
            response = HttpResponseServerError()
            del response['Content-Type']
            return response

    def read(self, request, **kwargs):

        return {'foo': 'bar'}
        # raise exceptions.NotImplemented()

    def get(self, request, obj=None, **kwargs):
        # TODO: caching, pagination
        # Delegate to `read` to actually grab a list of items
        items = self.read(request, **kwargs)

        # encode the list of read items.
        return self.encode(list(items))

    def post(self, request, obj, **kwargs):
        raise exceptions.NotImplemented()

    def put(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    def delete(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to.
        """
        pattern = '^{}{{}}(?:\.(?P<format>[^/]*?))?/?$'.format(self.name)
        return patterns('',
            url(pattern.format(''), self.dispatch, name='dispatch'),
            url(pattern.format('/(?P<id>.*)'), self.dispatch, name='dispatch')
        )


class Model(Resource):
    """Implementation of `Resource` for django's models.
    """
    #! The class object of the django model this resource is exposing.
    model = None

    def read(self, request, **kwargs):
        # TODO: filtering
        return self.model.objects.all()
