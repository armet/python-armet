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

    def find_encoder(self, request, **kwargs):
        """
        Determines the format to encode to and stores it upon success. Raises
        a proper exception if it cannot.
        """
        # Check locations where format may be defined in order of
        # precendence.
        if kwargs.get('format') is not None:
            # Format was provided through the URL via `.FORMAT`.
            self.encoder = encoders.get_by_name(kwargs['format'])

        else:
            # TODO: Should not have an else here and allow the header even
            # if the format check failed ?
            self.encoder = encoders.get_by_request(request)

        if self.encoder is None:
            # Failed to find an appropriate encoder
            # Get dictionary of available formats
            available = encoders.get_available()

            # TODO: No idea what to encode it with; using JSON for now
            # TODO: This should be a configurable property perhaps ?
            self.encoder = encoders.Json

            # encode the response using the appropriate exception
            raise exceptions.NotAcceptable(self.encode(available))

    def find_decoder(self, request, **kwargs):
        """
        Determines the format to decode to and stores it upon success. Raises
        a proper exception if it cannot.
        """
        self.decoder = decoders.get(request)
        if self.decoder is None:
            # Failed to find an appropriate decoder; we have no idea how to
            # handle the data.
            raise exceptions.UnsupportedMediaType()

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
            self.find_encoder(request, **kwargs)

            # TODO: Authn check
            # TODO: Authz check

            # By default, there is no object (for get and delete requests)
            obj = None
            if request.body:
                # Request a decode and proceed to decode the request.
                self.find_decoder(request)
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
        raise exceptions.NotImplemented()

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
