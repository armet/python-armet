import datetime
import warnings
from collections import OrderedDict, Iterable
from django import forms
from django.db.models.fields.related import RelatedField, RelatedObject
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import FieldDoesNotExist
from . import fields


class Resource(type):

    @staticmethod
    def ensure(attrs, name, default):
        if not attrs.get(name):
            attrs[name] = default

    @staticmethod
    def ensure_iterable(attrs, name):
        value = attrs.get(name)
        if value is not None \
                and not isinstance(value, Iterable) \
                or isinstance(value, basestring):
            attrs[name] = value,

    def __new__(cls, name, bases, attrs):
        # Ensure we have a valid name.
        cls.ensure(attrs, 'name', name.lower())

        # Initialize us to an empty iterable to simplify logic
        cls.ensure(attrs, 'relations', {})
        cls.ensure(attrs, 'filterable', ())
        cls.ensure(attrs, 'include', ())

        # We need to build our list of allowed HTTP methods
        name = 'http_allowed_methods'
        cls.ensure(attrs, 'http_list_allowed_methods', attrs[name])
        cls.ensure(attrs, 'http_detail_allowed_methods', attrs[name])

        # We need to build our list of allowed methods
        name = 'allowed_methods'
        cls.ensure(attrs, 'list_allowed_methods', attrs[name])
        cls.ensure(attrs, 'detail_allowed_methods', attrs[name])

        # Ensure fields that need to be iterable are iterable
        cls.ensure_iterable(attrs, 'http_allowed_methods')
        cls.ensure_iterable(attrs, 'http_list_allowed_methods')
        cls.ensure_iterable(attrs, 'http_detail_allowed_methods')
        cls.ensure_iterable(attrs, 'allowed_methods')
        cls.ensure_iterable(attrs, 'list_allowed_methods')
        cls.ensure_iterable(attrs, 'detail_allowed_methods')
        cls.ensure_iterable(attrs, 'fields')
        cls.ensure_iterable(attrs, 'include')
        cls.ensure_iterable(attrs, 'exclude')

        # Delegate to python to instantiate us.
        return super(Resource, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        if getattr(self, 'form', None) is not None:
            # Make a new fields list and discover any fields we can
            self._fields = OrderedDict()
            self.discover_fields()

            # Provide simple sanity checking..
            # Is the defined resource URI one of the found fields ?
            if self.resource_uri in self.fields:
                raise ImproperlyConfigured(
                    'The field name defined for the `resource_uri` (`{}`) '
                    'conflicts with a declared field on the resource.'.format(
                        self.resource_uri))

        # Delegate to python to finish us up.
        super(Resource, self).__init__(name, bases, attrs)

    def is_field_visible(self, name):
        visible = self.fields is not None and name not in self.fields
        visible = self.exclude is not None and name in self.exclude
        return visible

    def discover_fields(self):
        # Iterate through the list of declared fields using the provided form
        declared = getattr(self.form, 'declared_fields', {})
        meta = self.form._meta
        for name, item in declared.iteritems():
            if not self.is_field_visible(name):
                continue

            # Field is good and visible; instantiate and set initial
            # properties.
            field = fields.Field(name)
            field.clean = field.to_python
            field.relation = self.relations.get(name),
            field.filterable = name in self.filterable

            # Field is editable if it is not hidden from the bound form.
            if not meta.fields or name in meta.fields:
                if not meta.exclude or name not in meta.exclude:
                    field.editable = True

            # Field is a collection if it is some kind of
            # multiple choice field.
            field.collection = isinstance(item, forms.MultipleChoiceField) \
                or isinstance(item, forms.ModelMultipleChoiceField)

            # Determine python type of the field and store for later
            # reference; default is `str`.
            if isinstance(item, forms.DateField):
                field.type = datetime.date
            elif isinstance(item, forms.TimeField):
                field.type = datetime.time
            elif isinstance(item, forms.DateTimeField):
                field.type = datetime.datetime
            elif isinstance(item, forms.BooleanField):
                field.type = bool

            # Store constructed field.
            self._fields[name] = field

        # Append any 'extra' fields in the inclusion list
        for name in self.include:
            if name not in self._fields:
                self._fields = fields.Field(name,
                        relation=self.relations.get(name),
                        filterable=name in self.filterable,
                    )


class Model(Resource):

    def __new__(cls, name, bases, attrs):
        # Ensure we have a valid model form.
        # First check if we have a model form.
        if attrs.get('form'):
            if not issubclass(attrs['form'], forms.ModelForm):
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
            class form(forms.ModelForm):
                class Meta:
                    model = attrs['model']

            # Store the nicely generated one
            attrs['form'] = form

        # Ensure the slug is initially the pk field of the model
        cls.ensure(attrs, 'slug', attrs['model']._meta.pk.column)

        # Delegate to python to instantiate us.
        return super(Model, cls).__new__(cls, name, bases, attrs)

    def discover_fields(self):
        # Discover the fields explicitly declared on the model first.
        super(Model, self).discover_fields()

    # def is_related(self, field):
    #     if isinstance(field, RelatedField):
    #         return True

    #     if isinstance(field, RelatedObject):
    #         return self.is_related(field.field)

    #     return False

    # def is_direct(self, field):
    #     return not isinstance(field, RelatedObject)

    # def get_related_name(self, field):
    #     try:
    #         return field.get_accessor_name()
    #     except:
    #         return field.name

    # def get_field(self, name):
    #     try:
    #         return self.model._meta.get_field(name)

    #     except FieldDoesNotExist:
    #         # May still be a reverse relation field
    #         for obj in self.model._meta.get_all_related_objects():
    #             if obj.var_name == name:
    #                 return obj

    #         for obj in self.model._meta.get_all_related_many_to_many_objects():
    #             if obj.var_name == name:
    #                 return obj

    # def is_collection(self, name):
    #     if name in (x.name for x in self.model._meta.local_many_to_many):
    #         return True

    #     for obj in self.model._meta.get_all_related_many_to_many_objects():
    #         if obj.var_name == name:
    #             return obj

    # def get_parse(self, field):
    #     try:
    #         return field.field.to_python
    #     except:
    #         return field.to_python

    # def discover_fields(self):
    #     # Discover explicitly declared fields first.
    #     super(Model, self).discover_fields()

    #     # Discover additional model fields.
    #     if self.model is not None:

    #         for name in self.model._meta.get_all_field_names():
    #             # Iterate through the list of all ze fields
    #             field = self.get_field(name)
    #             if self.is_field_visible(name):
    #                 # Grab the relation if there is one
    #                 relation = self.relations.get(name)
    #                 related = self.is_related(field)
    #                 direct = self.is_direct(field)
    #                 hidden = False
    #                 related_name = self.get_related_name(field)
    #                 if not relation and related:
    #                     if direct:
    #                         # Field is a related model field but was not
    #                         # declared as a relation
    #                         continue
    #                     else:
    #                         hidden = True

    #                 # Determine properties of the field and store it
    #                 self.fields[name] = fields.Model(
    #                         collection=self.is_collection(name),
    #                         relation=relation,
    #                         filterable=name in self.filterable,
    #                         direct=direct,
    #                         hidden=hidden,
    #                         related_name=related_name,
    #                         parse=self.get_parse(field)
    #                     )
