from collections import OrderedDict, Sequence, Mapping
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.forms.models import model_to_dict
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
import six
from ..http import HttpResponse, constants
from .. import encoders, exceptions, decoders
from .. import utils
from . import meta


class Base(six.with_metaclass(meta.Resource)):

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

    #! Authentication object to proxy authentication requests to; leave
    #! unspecified for no authentication.
    authentication = None

    #! Authorization object to proxy authorization requests to; leave
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
    http_post_return_data = True

    #! Specifies that PUT should return data; defaults to False.
    http_put_return_data = True

    #! Name of the URL that is used in the url configuration.
    url_name = "api_dispatch"

    #! Whether to allow `create` on a `PUT` request.
    allow_create_on_put = False

    #! Whitelist of fields to allow through the preparation process.
    fields = None

    #! Blacklist of fields to disallow through the preparation process.
    exclude = None

    #! Additional fields to prepare from the source object or dictionary.
    include = None

    #! Validation hook to disable form validation.
    validation = True

    def filter(self, items):
        """Point of extension to filter the results returned from `read`."""
        # FIXME: Where should this go...
        return items

    @classmethod
    @csrf_exempt
    def view(cls, request, *args, **kwargs):
        try:
            # Are we authenticated; probably should check that now
            if cls.authentication is not None:
                user = None
                unauthenticated = HttpResponse(status=constants.FORBIDDEN)
                for auth in cls.authentication:
                    user = auth.authenticate(request)
                    if user is not None:
                        break

                    unauthenticated = auth.unauthenticated

                if user is not None:
                    # Cool; we're in -- set the request appropriately
                    request.user = user

                else:
                    # Died; bummer
                    return unauthenticated

            # Instantiate the resource to use for the cycle
            resource = cls(request,
                kwargs.get('id'),
                kwargs.get('components', '').split('/'))

            # Request an encoder as early as possible in order to
            # accurately return errors (if accrued).
            encoder = None
            encoder = encoders.find(request, kwargs.get('format'))
            if encoder is None:
                encoder = cls.default_encoder

            # Initiate the dispatch and return the response
            content = resource.dispatch()

            # Encode the content (if any) and return the response
            if content is not None:
                response = encoder.encode(content)
            else:
                response = HttpResponse()
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
                params=None
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

        #! Parameters are arguments in addition to the body or kwargs that
        #! overrides them both (for foriegn key navigation).
        self.params = params or {}

        #! A filterer needs to be made.
        self._filterer = self.filterer(self._fields) if self.filterer else None

    def dispatch(self):
        # Determine the method; returns our delegation function
        function = self.determine_method()

        # Check for initial accessiblity
        if self.authorization is not None \
                and not self.authorization.is_accessible(
                    self.request, self.method):
            # Failed pre-test; bail
            raise exceptions.Forbidden()

        # Grab the request data if we can
        data = None
        if self.request is not None and self.request.body:
            # Request a decoder and decode away
            data = decoders.find(self.request).decode(self.request)

            # Run the data through a clean cycle
            data = self.clean(data)

            # Check for authorization on the object if we have a real one
            if self.identifier is not None:
                # FIXME: We call `self.get()` frequently and special-case if
                #   we are directly accessing the resource..
                if self.authorization is not None \
                        and not self.authorization.is_authorized(
                            self.request, self.method, self.get()):
                    # Failed post-test; bail
                    raise exceptions.Forbidden()

        # Let's see how far down the rabbit hole we can go
        return self.traverse(self.process, function, data)

    def process(self, function, obj):
        # Execute the function found earlier
        response = function(obj)

        # If we got anything back ..
        if response is not None:
            # Run it through a preparation cycle
            return self.prepare(response)

        # Didn't get anything back; return nothing

    def traverse(self, process, method, obj):
        # We need to `traverse` down the rabbit hole to find the actual
        # resource we need to invoke the method on -- we don't need to
        # actually perform a `get` or anything; just keep recursing down
        if not self.components or not self.components[0]:
            # No fancy sub-resouce access or we are at the end;
            # just return ourself
            return process(method, obj)

        # We have at least one component
        name = self.components[0]
        field = self._fields.get(name)
        if name == self.resource_uri:
            # Just a URI
            return process(method, obj)

        if not field:
            # Field doesn't exist on this resource.
            raise exceptions.NotFound()

        if not field.relation:
            # This is a different (simple) kind of sub-resource access;
            # move along
            return process(method, obj)

        # Append to our param hash
        if self.params is None:
            self.params = OrderedDict()

        # FIXME: This method is a complete mess. re-write it

        params = dict(self.params)
        params[self.name] = self.identifier

        relation = field.relation

        if field.collection:
            if len(self.components) >= 2:
                identifier = self.components[1]
                splice = 2

            else:
                identifier = None
                splice = 1

            resource = relation(
                    request=self.request,
                    method=self.method,
                    identifier=identifier,
                    components=self.components[splice:],
                    params=params
                )

            # TODO: Stupid check needed here for those that forget
            # relation defines
            resource._fields[self.name].relation = self.__class__
        else:
            # Grab the object that we would have got
            item = self.get()
            relation = field.relation
            identifier = getattr(
                relation.resolve(getattr(item, name), self.request),
                    relation.slug)

            resource = relation(
                    request=self.request,
                    method=self.method,
                    identifier=identifier,
                    components=self.components[1:],
                    params=params
                )

        # Determine method here
        method = resource.determine_method()

        # Pass it through
        response = resource.traverse(resource.process, method, obj)
        self.status = resource.status
        return response

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
                    'message': 'operation not allowed on `{}`; see `allowed` '
                        'for allowed methods'.format(self.name),
                    'allowed': self.get_allowed_methods()
                })

    def determine_method(self):
        """Ensures HTTP method is acceptable."""
        # FIXME: This method should follow other conventions elsewhere:
        #   - `determine_http_method` as the name
        #   - should set self.request.method instead of self.method
        #   - probably should have an actual `determine_method` call as well
        #       to move error checking and authz earlier
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

    def clean(self, data):
        # Before the object goes anywhere its relations need to be resolved and
        # other things need to happen to make everything more python'y
        for name, field in self._fields.iteritems():
            value = data.get(name)
            if value is not None and field.relation is not None:
                data[name] = self.relation_clean(field, value)

            if value is None and field.default is not None:
                try:
                    data[name] = field.default()

                except:
                    data[name] = field.default

            if value is None and field.collection:
                data[name] = []

        # If this is a individual resource; we need to first get the
        # object being accessed; modify it according to the data, and pass
        # that into the form. This is done to allow both partial updates and
        # full updates to be done here.
        if self.identifier is not None:
            # Get the object being accessed as a data dictionary
            obj = self.get()

            # Update data dictionary with what was not (allowed to be)
            # provided
            for name, item in model_to_dict(obj).iteritems():
                if name not in self._fields or not self._fields[name].visible:
                    data[name] = item

        if self.validation:
            # Split data and files
            fields = self._fields
            files = {k: v for k, v in data.items() if fields[k].file}
            items = {k: v for k, v in data.items() if not fields[k].file}

            # Create a form instance to proxy validation
            form = self.form(data=items, files=files)

            # Attempt to validate the form
            if not form.is_valid():
                # We got invalid data; tsk.. tsk..; throw a bad request
                raise exceptions.BadRequest(form.errors)

            # We should have good, sanitized data now (thank you, forms)
            data = form.cleaned_data
            return data

        else:
            # No validation required; just return the data
            return data

    def relation_clean(self, field, value):
        if not isinstance(value, basestring):
            try:
                # Need to resolve all the values
                return [field.relation.resolve(x, self.request) for x in value]

            except TypeError:
                # Not an iterable; carry on.
                pass

        # Nope; should just be one that gets resolved
        return field.relation.resolve(value, self.request)

    @classmethod
    def resolve(cls, path, request, method='get', components=None, full=False):
        if path is None:
            # Come on.. return none
            return None

        try:
            # Attempt to resolve the path normally.
            resolution = resolve(path)
            resource = resolution.func.__self__(
                    request=request,
                    method=method,
                    identifier=resolution.kwargs['id'],
                    components=components
                )

            # Return our resolved object.
            return resource.get()

        except:
            # Assume we're already resolved
            return path

    def prepare(self, obj):
        if not isinstance(obj, Mapping):
            try:
                # Attempt to iterate and prepare each individual item as this
                # could easily be an iterable.
                return [self.item_prepare(x) for x in obj]

            except TypeError:
                pass

        # Just prepare the one item.
        response = self.item_prepare(obj)

        # # Are we accessing a sub-resource on this item?
        if self.components and self.components[0]:
            name = self.components[0]
            if name == self.resource_uri:
                # Just a resource URI; move along
                response = response[self.resource_uri]

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
        for name, field in self._fields.iteritems():
            # Is this visible first ?
            if not field.visible:
                # Nope; move along.
                continue

            # TODO: If we can refactor to avoid this ONE getattr call; speed
            #   of execution goes up by a factor of 10
            try:
                # Attempt to grab this field from the item.
                value = getattr(item, name)

            except:
                try:
                    # Maybe we have a dictionary
                    value = item.get(name)

                except:
                    # Something fun happened here.. ?
                    value = None

            # Run it through the `prepare_FOO` method (if defined).
            prepare = getattr(self, 'prepare_{}'.format(name), None)
            if prepare is not None:
                value = prepare(item, value)

            # Attempt to resolve the prepared value (which at this point
            # can be a callable)
            try:
                value = value()

            except:
                # Wasn't a callable; eh. move along
                pass

            # Is this perhaps a file
            if field.file:
                # Are we accessing it directly; if not, reverse it
                if self.components[0] != name:
                    value = self.reverse(item, components=name)

                else:
                    # Accessing it directly; return `JUST` the file
                    return {name: value}

            # Run it through the relation preparation method if we have
            # a relation.
            if field.relation is not None:
                try:
                    # Perhaps this is a many-to-many to models? Django gives us
                    # a model related manager
                    value = value.all()

                except:
                    # Guess not; move along
                    pass

                # Attempt to resolve the related field; we need to transform
                # the object to its URI.
                try:
                    # Attempt to iterate over each item to resolve it.
                    value = [field.relation.reverse(x) for x in value]

                except TypeError:
                    # Not iterable; reverse the one.
                    value = field.relation.reverse(value)

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

    @classmethod
    def reverse(cls, item, components=None):
        # Build our argument list for django's url resolver
        kwargs = {'resource': cls.name}

        if components is not None:
            kwargs['components'] = components

        if item is not None:
            try:
                # Attempt to get the identifier of the item; treat it as an
                # dictionary
                if cls.slug in item:
                    kwargs['id'] = item[cls.slug]

            except:
                try:
                    # Let's try direct access -- maybe we have an object
                    kwargs['id'] = getattr(item, cls.slug)

                except:
                    # We'll damn; item must be just an id (hopefully)
                    kwargs['id'] = item

        else:
            # We have no item; return nothing.
            return None

        # Pass this along to django's URL resolver; it should figure the
        # rest out for us.
        return reverse(cls.url_name, kwargs=kwargs)

    def get(self, obj=None):
        # Ensure we're allowed to read
        self.assert_method_allowed('read')

        try:
            # Delegate to `read` to actually grab a list of items.
            response = self.read()

        except:
            # Something went wrong; were gone
            raise exceptions.NotFound()

        # Invoke a filter function if available.
        response = self.filter(response)

        if self.identifier is None and self._filterer is not None:
            # Invoke our filterer (if we have one) to filter our response using
            # the query string.
            response = self._filterer.filter(response, self.request.GET)

        if self.identifier is not None:
            if not response:
                # If we were attempting to retrieve a single resource and we
                # didn't get one; throw a 404.
                raise exceptions.NotFound()

            if not isinstance(response, basestring) \
                    and not isinstance(response, Mapping):
                # Return only the one object.
                response = response[0]

        # Return our (maybe filtered) response.
        return response

    def post(self, obj):
        # Ensure we're allowed to create
        self.assert_method_allowed('create')

        if self.identifier is None:
            # Set our status initially so `create` can change it
            self.status = constants.CREATED

            # Delegate to `create` to actually create a new item.
            response = self.create(obj)

            if self.http_post_return_data:
                # We're supposed to return our data; so, well, return it
                return response

            # Don't return a thing normally

        else:
            # Attempting to create a sub-resource; go away (for now)
            # TODO: What are we supposed to do here..
            raise exceptions.NotImplemented()

    def put(self, data):
        if self.identifier is None:
            # Attempting to change everything; go away (for now)
            raise exceptions.NotImplemented()

        else:
            try:
                # Coerce the object
                obj = self.get()

            except:
                # Bad; we're not here
                obj = None

            if obj is not None:
                # Set our status initially so `create` can change it
                self.status = constants.OK

                # Ensure we're allowed to update (but not read, hehe)
                self.assert_method_allowed('update')

                # Send us off to create
                response = self.update(obj, data)

            elif self.allow_create_on_put:
                # Set our status initially so `create` can change it
                self.status = constants.CREATED

                # Ensure we're allowed to create
                self.assert_method_allowed('create')

                # Send us off to create
                response = self.create(data)

            else:
                # Not allowed to create on put; damn
                raise exceptions.NotImplemented()

            # Do we return data ?
            if not self.http_put_return_data:
                # We're not supposed to return our data; so, well, return it
                if self.status != constants.CREATED:
                    self.status = constants.NO_CONTENT

            else:
                return response

    def delete(self, obj=None):
        if self.identifier is None:
            # Attempting to delete everything; go away (for now)
            raise exceptions.NotImplemented()

        else:
            # Set our status initially so `destory` can change it
            self.status = constants.NO_CONTENT

            # Delegate to `destroy` to actually delete the item.
            self.destroy(self.get())

    def read(self):
        # No sane defaults for cRud exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def create(self, obj):
        # No sane defaults for Crud exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def update(self):
        # No sane defaults for crUd exist on this base, abstract resource.
        raise exceptions.NotImplemented()

    def destroy(self):
        # No sane defaults for cruD exist on this base, abstract resource.
        raise exceptions.NotImplemented()
