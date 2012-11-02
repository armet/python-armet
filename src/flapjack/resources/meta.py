import warnings
from collections import OrderedDict, Iterable
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.db.models import ManyToManyField, FileField
from .. import fields


class Resource(type):

    @staticmethod
    def ensure(attrs, name, default):
        if not attrs.get(name):
            attrs[name] = default

    @staticmethod
    def ensure_iterable(attrs, name, force=False):
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
        if attrs.get(name):
            cls.ensure(attrs, 'http_list_allowed_methods', attrs[name])
            cls.ensure(attrs, 'http_detail_allowed_methods', attrs[name])

        # We need to build our list of allowed methods
        name = 'allowed_methods'
        if attrs.get(name):
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
        cls.ensure_iterable(attrs, 'authentication')
        # cls.ensure_iterable(attrs, 'authorization') ?

        # Delegate to python to instantiate us.
        return super(Resource, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):
        if getattr(self, 'form', None) is None:
            # No form declared; just use one
            self.form = forms.Form

        # Make a new fields list and discover any fields we can
        self._fields = OrderedDict()
        self.discover_fields()

        # Provide simple sanity checking..
        # Is the defined resource URI one of the found fields ?
        resource_uri = getattr(self, 'resource_uri', None)
        if resource_uri in self._fields:
            raise ImproperlyConfigured(
                'The field name defined for the `resource_uri` (`{}`) '
                'conflicts with a declared field on the resource.'.format(
                    resource_uri))

        # Delegate to python to finish us up.
        super(Resource, self).__init__(name, bases, attrs)

    def is_field_visible(self, name):
        if self.fields is not None and name not in self.fields \
                or self.exclude is not None and name in self.exclude:
            return False

        return True

    def discover_fields(self):
        # Iterate through the list of declared fields using the provided form
        declared = getattr(self.form, 'declared_fields', {})
        meta = getattr(self.form, '_meta', None)
        for name, item in declared.iteritems():
            # Instantiate and set initial properties.
            field = fields.Field(name, relation=self.relations.get(name))
            field.clean = item.to_python
            field.filterable = name in self.filterable
            field.visible = self.is_field_visible(name)

            # Are we dealing with a file field ?
            if isinstance(item, forms.FileField):
                field.file = True

            # Field is editable if it is not hidden from the bound form.
            if not meta.fields or name in meta.fields:
                if not meta.exclude or name not in meta.exclude:
                    field.editable = True

            # Field is a collection if it is some kind of
            # multiple choice field.
            field.collection = isinstance(item, forms.MultipleChoiceField) \
                or isinstance(item, forms.ModelMultipleChoiceField)

            # Store constructed field.
            self._fields[name] = field

        # Append any 'extra' fields in the inclusion list
        for name in self.include:
            if name not in self._fields:
                self._fields[name] = fields.Field(name,
                        relation=self.relations.get(name),
                        filterable=name in self.filterable,
                        visible=self.is_field_visible(name)
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
        if attrs.get('model'):
            cls.ensure(attrs, 'slug', attrs['model']._meta.pk.column)

        # Delegate to python to instantiate us.
        return super(Model, cls).__new__(cls, name, bases, attrs)

    def discover_fields(self):
        # Discover the fields explicitly declared on the model first.
        super(Model, self).discover_fields()

        if getattr(self, 'model', None) is None:
            # No model so we're done here
            return

        # Discover additional fields declared on the model.
        meta = self.model._meta
        for name in meta.get_all_field_names():
            # Initial declaration of field properties
            props = {
                    'visible': self.is_field_visible(name),
                    'filterable': True
                }

            try:
                # Get the field object from the model.
                item = meta.get_field(name)

            except FieldDoesNotExist:
                # Not a direct field; but, may be a reverse relation.
                for obj in meta.get_all_related_objects():
                    if obj.var_name == name:
                        # Found a reverse relation; record and get out
                        item = obj.field
                        name = obj.get_accessor_name()
                        break

                else:
                    for obj in meta.get_all_related_many_to_many_objects():
                        if obj.var_name == name:
                            # Found a m2m reverse relation; record and get out
                            item = obj.field
                            name = obj.get_accessor_name()
                            props['collection'] = True
                            break

            # Attempt to get the relation for the field
            relation = self.relations.get(name)
            if relation:
                props['relation'] = relation

            elif isinstance(item, RelatedField):
                # No defined relation; the field doesn't exist
                continue

            # Discover any properties from the field
            props['file'] = isinstance(item, FileField)
            props['clean'] = item.to_python
            props['editable'] = item.editable or item.auto_created
            props['default'] = item.default
            props['collection'] = props.get('collection', False) \
                or isinstance(item, ManyToManyField)

            # Store the field
            self._fields[name] = fields.Model(name, **props)
