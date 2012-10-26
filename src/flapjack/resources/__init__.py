# coding=utf-8
""" ..
"""
from collections import Sequence
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from ..http import HttpResponse, constants
from .. import encoders, exceptions, decoders
from .meta import Model, Resource
from collections import OrderedDict
# from . import authentication as authn
# from . import authorization as authz
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

    #! Name of the field on the response object to use as the slug in the
    #! resource URI for resolution and reversal of URIs.
    slug = 'id'

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
                kwargs.get('components', '').split('/'))

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            encoder = None
            encoder = encoders.find(request, kwargs.get('format'))

            # Initiate the dispatch and return the response
            content = resource.dispatch()

            # Encode the content (if any) and return the response
            if content is None:
                response = HttpResponse()
            else:
                response = encoder.encode(content)
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

    def __init__(self,
                request=None,
                identifier=None,
                components=None,
                method=None,
            ):
        """Initialize ourself and prepare for the dispatch process."""
        #! Status of the request cycle.
        self.status = constants.OK

        #! Method to override anything said in the request object (
        #! used to allow resources to call themselves and shortcircuit in
        #! the case of resolution).
        self.method = method

        #! Django request object.
        self.request = request

        #! Identifier indicating we are accessing an individual resource.
        self.identifier = identifier

        #! Components list that is for sub resource resolution.
        self.components = components

    def dispatch(self):
        # Determine the method; returns our delegation function
        method = self.determine_method()

        # Grab the request object if we can
        obj = None
        if self.request is not None and self.request.body:
            # Request a decoder and decode away
            obj = decoders.find(self.request).decode(self.request)

            # Run the object through a clean cycle
            obj = self.clean(obj)

        # Execute the function found earlier
        response = method(obj)

        # If we got anything back ..
        if response is not None:
            # Run it through a preparation cycle
            return self.prepare(response)

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

    def get_allowed_methods(self):
        """Gets list of allowed methods for the current request."""
        if self.identifier is not None:
            return self.detail_allowed_methods
        else:
            return self.list_allowed_methods

    def is_method_allowed(self, method):
        """Checks if the passed is an allowed method."""
        return method in self.get_allowed_methods()

    def assert_method_allowed(self, method):
        """Asserts that the passed is an allowed method."""
        if not self.is_method_allowed(method):
            raise exceptions.Forbidden({
                    'message': 'operation not allowed; see `allowed` '
                        'for allowed methods',
                    'allowed': self.get_allowed_methods()
                })

    def determine_method(self):
        """Ensures HTTP method is acceptable."""
        if self.method is None:
            # Method override wasn't set; determine the HTTP method.
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

    def clean(self, obj):
        # Before the object goes anywhere its relations need to be resolved and
        # other things need to happen to make everything more python'y
        for name, field in self.fields.iteritems():
            value = obj.get(name)
            if value is not None and field.relation is not None:
                obj[name] = self.relation_clean(field, value)

        # Create a form instance to proxy validation
        form = self.form(data=obj)

        # Attempt to validate the form
        if not form.is_valid():
            # We got invalid data; tsk.. tsk..; throw a bad request
            raise exceptions.BadRequest(form.errors)

        # We should have good, sanitized data now (thank you, forms)
        return form.cleaned_data

    def relation_clean(self, field, value):
        if not isinstance(value, basestring):
            try:
                # Need to resolve all the values
                return [field.relation.resolve(x) for x in value]

            except TypeError:
                # Not an iterable; carry on.
                pass

        # Nope; should just be one that gets resolved
        return field.relation.resolve(value)

    @classmethod
    def resolve(cls, path, method='get', components=None, full=False):
        try:
            # Attempt to resolve the path normally.
            resolution = resolve(path)
            resource = resolution.func.__self__(
                    method=method,
                    identifier=resolution.kwargs['id'],
                    components=components
                )

            # Return our resolved object.
            return resource.dispatch()

        except:
            # Assume we're already resolved
            return path

    def prepare(self, obj):
        try:
            # Attempt to iterate and prepare each individual item as this could
            # easily be an iterable.
            return [self.item_prepare(x) for x in obj]

        except TypeError:
            # Not iterable; we have but one.
            pass

        # Just prepare the one item.
        response = self.item_prepare(obj)

        # Are we accessing a sub-resource on this item?
        if self.components and self.components[0]:
            name = self.components[0]
            field = self.fields.get(name)
            if name == self.resource_uri:
                # Just a resource URI; move along
                response = response[self.resource_uri]

            else:
                if field is None or field.collection:
                    # Sub-relation not found
                    raise exceptions.NotFound()

                if field.relation is not None:
                    # Related field; send it back through dispatch
                    response = field.relation.resolve(path=response[name],
                            method=self.method,
                            components=self.components[1:],
                            full=True
                        )

                else:
                    # Simple access; move along
                    response = response[name]

        # Pass us along.
        return response

    def item_prepare(self, item):
        # Initialize the item object; we like to remember the order of the
        # fields.
        obj = OrderedDict()

        # Append the URI at the beginning.
        obj[self.resource_uri] = self.reverse(item)

        # Iterate through the fields and build the object from the item.
        for name, field in self.fields.iteritems():
            # Attempt to grab this field from the item.
            # TODO: If we can refactor to avoid this ONE getattr call; speed
            #   of execution goes up by a factor of 10
            value = getattr(item, name, None)

            # Run it through the `prepare_FOO` method (if defined).
            prepare = self.__dict__.get('prepare_{}'.format(name))
            if prepare is not None:
                value = prepare(value)

            # Attempt to resolve the prepared value (which at this point
            # can be a callable)
            try:
                value = value()

            except:
                # Wasn't a callable; eh. move along
                pass

            # Run it through the relation preparation method if we have
            # a relation.
            if field.relation is not None:
                value = self.relation_prepare(value, field.relation)

            # Ensure we "always" have an iterable for a collection field
            if field.collection:
                if value is None:
                    # Nothing returned should be serialized as an empty array.
                    value = []

                elif isinstance(value, basestring) \
                        or not isinstance(value, Sequence):
                    # We're not a sequence; make us one.
                    value = value,

            # Set us on the result object (finally)
            obj[name] = value

        # Pass our object back
        return obj

    def relation_prepare(self, value, relation):
        try:
            # Perhaps this is a many-to-many to models? Django gives us
            # a model related manager instead of anything pyhton'y
            value = value.all()
        except:
            # Guess not; move along
            pass

        # Attempt to resolve the related field; we need to transform the
        # object to its URI.
        try:
            # Attempt to iterate over each item to resolve it.
            return [relation.reverse(x) for x in value]

        except TypeError:
            # Not iterable; reverse the one.
            return relation.reverse(value)

    @classmethod
    def reverse(cls, item):
        # Build our argument list for django's url resolver
        kwargs = {'resource': cls.name}

        if item is not None:
            try:
                # Attempt to get the identifier of the item; treat it as an
                # dictionary
                if cls.slug in item:
                    kwargs['id'] = item[cls.slug]

            except:
                # Well; that was a flop...
                pass

            try:
                # Let's try direct access -- maybe we have an object
                kwargs['id'] = getattr(item, cls.slug)

            except:
                # We'll damn; item must be just an id (hopefully)
                kwargs['id'] = item

        # Pass this along to django's URL resolver; it should figure the
        # rest out for us.
        return reverse(cls.url_name, kwargs=kwargs)

    def get(self, obj=None):
        # Ensure we're allowed to read
        self.assert_method_allowed('read')

        # Delegate to `read` to actually grab a list of items.
        response = self.read()

        # TODO: Invoke our filterer (if we have one) to filter our response
        # if self.filterer is not None:
        #     response = self.filterer.filter(response, self.request.GET)

        # Return our (maybe filtered) response.
        return response

    def post(self, obj):
        if self.identifier is None:
            # Ensure we're allowed to create
            self.assert_method_allowed('create')

            # Set our status initially so `create` can change it
            self.status = constants.CREATED

            # Delegate to `create` to actually create a new item.
            response = self.create(obj)

            if self.http_post_return_data:
                # We're supposed to return our data; so, well, return it
                return response

            # Don't return a thing normally

        else:
            # Attempting to create a sub-resource; go away
            # TODO: What are we supposed to do here..
            raise exceptions.NotImplemented()

    def put(self, obj):
        raise exceptions.NotImplemented()

    def delete(self, obj=None):
        if self.identifier is None:
            # Attempting to delete everything; go away
            raise exceptions.NotImplemented()

        else:
            # Set our status initially so `destory` can change it
            self.status = constants.NO_CONTENT

            # Delegate to `destroy` to actually delete the item.
            self.destroy()

    def read(self):
        # No sane defaults for cRud exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def create(self):
        # No sane defaults for Crud exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def update(self):
        # No sane defaults for crUd exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def destroy(self):
        # No sane defaults for cruD exist on this base, abstract resource.
        raise exceptions.NotImplemented()


class Model(six.with_metaclass(Model, Resource)):
    """Implementation of a `RESTful` resource using django models.
    """

    #! Model class object to use to bind to this resource.
    #! Is overridden by the model option in the ModelForm form if specified.
    model = None

    @classmethod
    def resolve(cls, path, full=False, **kwargs):
        # Delegate to the base resource to do the actual resolution
        resolution = super(Model, cls).resolve(path, **kwargs)

        if not full:
            try:
                # Attempt to grab the slug from the resolution as an object;
                # The normal path (ChoiceField) expects the entire resolved
                # resource but (ModelChoiceField) expects only the pk
                return resolution[cls.model._meta.pk.name]

            except:
                # Wasn't a model apparently; just return the resolution
                pass

        # Pass us on
        return resolution

    @utils.classproperty
    @utils.memoize
    def queryset(cls):
        """Queryset that is used to read and filter data."""
        return cls.model.objects.all

    def read(self):
        """Implementation of `read` using django models."""
        if self.identifier is not None:
            try:
                # This is an individual resource; attempt to get it
                return self.queryset().get(**{self.slug: self.identifier})

            except:
                # Well damn; we don't have one -- die
                raise exceptions.NotFound()

        else:
            # Just get them all; hehehe..
            return self.queryset()

    def create(self, obj):
        # Iterate through and set all fields that we can initially
        params = {}
        for field in self.fields.values():
            if field.name not in obj:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection:
                # This is a m2m field; move along for now
                continue

            # This is not a m2m field; we can set this now
            params[field.name] = obj[field.name]

        # Perform the initial create
        model = self.model.objects.create(**params)

        # Iterate through again and set the m2m bits
        for field in self.fields.values():
            if field.name not in obj:
                # Isn't here; move along
                continue

            if field.relation is not None and field.collection:
                # This is a m2m field; we can set this now
                setattr(model, field.name, obj[field.name])

        # Perform a final save
        model.save()

        # Return the fully constructed model
        return model

    def update(self):
        # Nothing here yet..
        pass

    def destroy(self):
        # Delegate to django to perform the creation
        self.model.objects.get(**{self.slug: self.identifier}).delete()
