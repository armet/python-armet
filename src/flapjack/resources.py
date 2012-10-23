""" ..
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.utils.functional import cached_property
from . import emitters, exceptions, parsers


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

    def __init__(self):
        # Initialize name to be the name of the instantiated class if it was
        # not defined in the class definition.
        if self.name is None:
            self.name = self.__class__.__name__.lower()

    def find_emitter(self, request, **kwargs):
        """
        Determines the format to emit to and stores it upon success. Raises
        a proper exception if it cannot.
        """
        # Check locations where format may be defined in order of
        # precendence.
        if kwargs.get('format') is not None:
            # Format was provided through the URL via `.FORMAT`.
            self.emitter = emitters.get_by_name(kwargs['format'])

        else:
            # TODO: Should not have an else here and allow the header even
            # if the format check failed ?
            self.emitter = emitters.get_by_request(request)

        if self.emitter is None:
            # Failed to find an appropriate emitter
            # Get dictionary of available formats
            available = emitters.get_available()

            # TODO: No idea what to emit it with; using JSON for now
            # TODO: This should be a configurable property perhaps ?
            self.emitter = emitters.Json

            # Emit the response using the appropriate exception
            raise exceptions.NotAcceptable(self.emit(available))

    def find_parser(self, request, **kwargs):
        """
        Determines the format to parse to and stores it upon success. Raises
        a proper exception if it cannot.
        """
        self.parser = parsers.get(request)
        if self.parser is None:
            # Failed to find an appropriate parser; we have no idea how to
            # handle the data.
            raise exceptions.UnsupportedMediaType()

    def emit(self, obj=None, status=200):
        """Transforms python objects to an acceptable format for tansmission.
        """
        response = HttpResponse(status=status)
        if obj is not None:
            response.content = self.emitter.emit(obj)
            response['Content-Type'] = self.emitter.get_mimetype()
        else:
            # No need to specify the default content-type if we don't
            # have a body.
            del response['Content-Type']
        return response

    def parse(self, request):
        """Transforms recieved data to valid python objects.
        """
        # TODO: anything else to do here ?
        return self.parser.parse(request)

    # TODO: add some magic to make this a class method
    @cached_property
    def allow_header(self):
        allow = [m.upper() for m in self.http_allowed_methods]
        return ', '.join(allow).strip()

    def find_method(self, method):
        """Ensures method is acceptable; throws appropriate exception elsewise.
        """
        method_name = method.lower()
        if method_name not in self.http_method_names:
            # Method not understood by our library.  Die.
            response = HttpResponse()
            raise exceptions.NotImplemented(response)

        method = getattr(self, method_name, None)
        if method_name not in self.http_allowed_methods or method is None:
            # Method understood but not allowed.  Die.
            response = HttpResponse()
            response['Allow'] = self.allow_header()
            raise exceptions.MethodNotAllowed(response)

        # Method is allowed, continue.
        return method

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # ..
        try:
            # Ensure the request method is present in the list of
            # allowed HTTP methods
            method = self.find_method(request.method)

            # Request an emitter as early as possible in order to
            # accurately return errors (if accrued).
            self.find_emitter(request, **kwargs)

            # TODO: Authn check
            # TODO: Authz check

            # By default, there is no object (for get and delete requests)
            obj = None
            if request.body:
                # Request a parse and proceed to parse the request.
                self.find_parser(request)
                obj = self.parse(request)

                # TODO: Authz check (w/object)

            # Delegate to an appropriate method
            method(request, obj, *args, **kwargs)

            # DEBUG: Returning just what we got
            return self.emit()

        except exceptions.Error as ex:
            # TODO: We need to emit the error response.
            return ex.response

    def get(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    def post(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    def put(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    def delete(self, request, obj, *args, **kwargs):
        raise exceptions.NotImplemented()

    # TODO: add some magic to make this a class method
    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to.
        """
        pattern = '^{}{{}}(?:\.(?P<format>[^/]*?))?/?$'.format(self.name)
        return patterns('',
            url(pattern.format(''), self.dispatch, name='dispatch'),
            url(pattern.format('/(?P<id>.*)'), self.dispatch, name='dispatch')
        )
