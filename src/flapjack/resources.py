""" ..
"""
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.utils.functional import cached_property
from django.conf import settings
from django.core.urlresolvers import reverse, resolve
from django.forms import Form, ModelForm, MultipleChoiceField
from django.db.models import ForeignKey, ManyToManyField
from .http import HttpResponse
from . import encoders, exceptions, decoders, fields
# from . import authentication as authn
# from . import authorization as authz
import six


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

        # Ensure we have an empty relations dict if none was defined
        if hasattr(cls, 'relations') and cls.relations is None:
            cls.relations = {}

        if hasattr(cls, 'Form'):
            # Allow the form to be specified as a sub-class
            cls.form = cls.Form

        # Initialize listing of fields
        cls._fields = {}

        # Generate the list of fields using the provided form
        if hasattr(getattr(cls, 'form', None), 'declared_fields'):
            # Iterate through each declared field on the form
            for name, field in cls.form.declared_fields.items():
                if cls._is_visible(name):
                    # Determine field properties
                    props = {'collection': isinstance(
                        field, MultipleChoiceField)}

                    if name in cls.relations:
                        # Field is some kind of relation and
                        # is declared by the resource; add it
                        cls._fields[name] = fields.Related(
                            name, cls.relations[name], **props)

                    else:
                        # Field has been declared visible; construct it
                        # and add it to our list
                        cls._fields[name] = fields.Field(name, **props)

        # Delegate to python magic to initialize the class object
        super(DeclarativeResource, cls).__init__(name, bases, attributes)


class Resource(six.with_metaclass(DeclarativeResource)):

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

            # We start off with a successful response; let's see what happens..
            self.status = 200

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

                # Run through form clean cycle
                request_obj = self.clean(request_obj)

                # TODO: Authz check (w/obj)

            # Delegate to an appropriate method to grab the response;
            items = function(request_obj, kwargs.get('id'), **request.GET)
            if items is not None:
                # Run items through prepare cycle
                response_obj = self.prepare(items)

                # Encode and the object into a response
                response = self.encoder.encode(response_obj)
                response.status_code = self.status
                response['Location'] = self.reverse(response_obj.get('id'))

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
                kwargs['id'] = item['id']
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
        obj = {}
        for name, field in self._fields.items():
            # Constuct object containing all properties
            # from the item
            obj[name] = getattr(item, name, None)

            # Run it through the (optional) prepare_FOO function
            prepare_foo = getattr(self, 'prepare_{}'.format(name), None)
            if prepare_foo is not None:
                obj[name] = prepare_foo(obj[name])

            if isinstance(field, fields.Related) and obj[name] is not None:
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

        return obj

    def prepare(self, items):
        try:
            # Attempt to iterate and prepare each item
            objs = {}
            for item in items:
                obj = self._prepare_item(item)
                uri = self.reverse(obj)
                objs[uri] = obj
            return objs
        except TypeError:
            # Not iterable; we only have one
            return self._prepare_item(items)

    def clean(self, obj):
        # Before the object goes anywhere its relations need to be resolved.
        for field in self._fields.values():
            if field.name in obj:
                if isinstance(field, fields.Related):
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

    @cached_property
    def urls(self):
        """Constructs the URLs that this resource will respond to."""
        #! In order to undo a reverse() call (to get the resource from a slug),
        #! call django.core.urlresolvers.resolve(slug).  the resulting object's
        #! func attribute is the entrypoint into the resource.  So, to get the
        #! resource object, simply
        #! django.core.urlresolvers.resolve(slug).func.__self__
        pattern = '^{}{{}}/??(?:\.(?P<format>[^/]*?))?/?$'.format(self.name)
        name = 'api_dispatch'
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
        model_class = getattr(cls, 'model', None)
        if model_class is not None:
            if not issubclass(getattr(cls, 'form', None), ModelForm):
                # Construct a form class that is bound to our model
                class Form(ModelForm):
                    class Meta:
                        model = model_class

                # Declare our use of the form class
                cls.form = Form

            # Iterate through each declared field on the model
            #model_fields = []
            model_fields = list(cls.model._meta.local_fields)
            model_fields += list(cls.model._meta.local_many_to_many)
            for field in model_fields:
                if cls._is_visible(field.name):
                    if field.name not in cls._fields:
                        # Gather properties for the field
                        props = {
                                'editable': field.editable,
                                'collection': isinstance(field,
                                    ManyToManyField)
                            }

                        relation = cls.relations.get(field.name)
                        if relation is not None:
                            # Field is a foreignkey and its relation
                            # is declared by the resource; add it
                            cls._fields[field.name] = fields.Related(
                                field.name, relation, **props)

                        if isinstance(field, ForeignKey):
                            # Field is a related model field but was not
                            # declared as a relation
                            continue

                        if isinstance(field, ManyToManyField):
                            # Field is a related model field but was not
                            # declared as a relation
                            continue

                        else:
                            # Field is visible and not already declared
                            # explicitly by the model; add it to our list
                            cls._fields[field.name] = fields.Field(field.name,
                                editable=field.editable)


class Model(six.with_metaclass(DeclarativeModel, Resource)):
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
            except self.model.DoesNotExist:
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

            if isinstance(field, fields.Related) and field.collection:
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

            if isinstance(field, fields.Related) and field.collection:
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
