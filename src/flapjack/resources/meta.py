import warnings
from collections import OrderedDict, Iterable
#from django.utils.functional import cached_property
from django.forms import MultipleChoiceField, ModelForm
from django.db.models.fields.related import RelatedField, RelatedObject
from django.core.exceptions import ImproperlyConfigured
from . import fields
from django.db.models.fields import FieldDoesNotExist


class Resource(type):

    @staticmethod
    def coerce_allowed(attrs, name, defualt):
        if not attrs.get(name):
            attrs[name] = attrs[defualt]

        if not isinstance(attrs[name], Iterable) \
                or isinstance(attrs[name], basestring):
            # Always coerce these to be lists
            attrs[name] = attrs[name],

    def __new__(cls, name, bases, attrs):
        # Ensure we have a valid name.
        if not attrs.get('name'):
            # Defaults to the lowercase'd class name.
            attrs['name'] = name.lower()

        if not attrs.get('relations'):
            # Initialize us to an empty dictionary to simplify logic
            attrs['relations'] = {}

        if not attrs.get('filterable'):
            # Initialize us to an empty dictionary to simplify logic
            attrs['filterable'] = {}

        # We need to build our list of allowed HTTP methods
        name = 'http_allowed_methods'
        if attrs.get(name):
            cls.coerce_allowed(attrs, 'http_list_allowed_methods', name)
            cls.coerce_allowed(attrs, 'http_detail_allowed_methods', name)

        # We need to build our list of allowed methods
        name = 'allowed_methods'
        if attrs.get(name):
            cls.coerce_allowed(attrs, 'list_allowed_methods', name)
            cls.coerce_allowed(attrs, 'detail_allowed_methods', name)

        # Delegate to python to instantiate us.
        return super(Resource, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        form = getattr(self, 'form', None)
        if form is not None:
            # Make a new fields list
            self.fields = OrderedDict()

            # A form as been declared; discover its fields
            self.discover_fields()

            try:
                # Instantiate anything that needs it
                self._filterer = self.filterer(self.fields)

            except TypeError:
                # Filterer wasn't defined because it didn't want to be.
                self._filterer = None
                pass

            # Is the defined resource URI one of the found fields ?
            if self.resource_uri in self.fields:
                # Yes; die
                raise ImproperlyConfigured(
                    'The field name defined for the `resource_uri` (`{}`) '
                    'conflicts with a declared field on the resource.'.format(
                        self.resource_uri))

        # Delegate to python to finish us up.
        super(Resource, self).__init__(name, bases, attrs)

    def is_field_visible(self, name):
        """Discover if a field is visible."""
        whitelist = self.form._meta.fields
        if whitelist is not None and name not in whitelist:
            # There is a whitelist present on the bound form; this field
            # is not declared in it.
            return False

        blacklist = self.form._meta.exclude
        if blacklist is not None and name in blacklist:
            # There is a blacklist present on the bound form; this field
            # is declared in it.
            return False

        # Field is good and visible.
        return True

    def discover_fields(self):
        # Iterate through the list of fields using the provided form
        for name, field in getattr(self.form, 'declared_fields', {}).items():
            if self.is_field_visible(name):
                # Determine properties of the field
                self.fields[name] = fields.Field(
                        collection=isinstance(field, MultipleChoiceField),
                        relation=self.relations.get(name),
                        filterable=self.filterable.get(name)
                    )


class Model(Resource):

    def __new__(cls, name, bases, attrs):
        # Ensure we have a valid model form.
        # First check if we have a model form.
        if attrs.get('form'):
            if not issubclass(attrs['form'], ModelForm):
                # Found a form; wasn't a model form -- tell the user to RTFM.
                raise ImproperlyConfigured('Use of a model resource requires '
                    "'form' to be a model form.")

            elif 'model' in attrs:
                # Let the user know this is unneccessary -- form overrides it
                warnings.warn("'model' is overriden by 'form'; "
                    "there is no need to declare 'model'.")

            # Ensure model is set properly for easier access
            attrs['model'] = attrs['form']._meta.model

        elif 'model' in attrs:
            # Form wasn't declared; be nice and auto-generate a class
            # for them.
            class form(ModelForm):
                class Meta:
                    model = attrs['model']

            # Store the nicely generated one
            attrs['form'] = form

        if attrs.get('model'):
            # Ensure the slug is initially the pk field of the model
            attrs['slug'] = attrs['model']._meta.pk.column

        # Delegate to python to instantiate us.
        return super(Model, cls).__new__(cls, name, bases, attrs)

    def is_related(self, field):
        if isinstance(field, RelatedField):
            return True

        if isinstance(field, RelatedObject):
            return self.is_related(field.field)

        return False

    def get_field(self, name):
        try:
            return self.model._meta.get_field(name)
        except FieldDoesNotExist:
            # May still be a reverse relation field
            for obj in self.model._meta.get_all_related_objects():
                if obj.var_name == name:
                    return obj

            for obj in self.model._meta.get_all_related_many_to_many_objects():
                if obj.var_name == name:
                    return obj

    def discover_fields(self):
        # Discover explicitly declared fields first.
        super(Model, self).discover_fields()

        # Discover additional model fields.
        if self.model is not None:
            m2m = [x.name for x in self.model._meta.local_many_to_many]
            for name in self.model._meta.get_all_field_names():
                # Iterate through the list of all ze fields
                field = self.get_field(name)
                print(self.name, name, field)
                if self.is_field_visible(name):
                    # Grab the relation if there is one
                    relation = self.relations.get(name)
                    related = self.is_related(field)
                    if not relation and related:
                        # Field is a related model field but was not
                        # declared as a relation
                        continue

                    # Determine properties of the field and store it
                    self.fields[name] = fields.Model(
                            collection=name in m2m,
                            relation=relation,
                            filterable=self.filterable.get(name)
                        )
