import warnings
from collections import OrderedDict
#from django.utils.functional import cached_property
from django.forms import MultipleChoiceField, ModelForm
from django.db.models.fields.related import RelatedField
from django.core.exceptions import ImproperlyConfigured
from . import fields


class Resource(type):

    def __new__(cls, name, bases, attributes):
        # Ensure we have a valid name.
        if not attributes.get('name'):
            # Defaults to the lowercase'd class name.
            attributes['name'] = name.lower()

        if not attributes.get('relations'):
            # Initialize us to an empty dictionary to simplify logic
            attributes['relations'] = {}

        if not attributes.get('filterable'):
            # Initialize us to an empty dictionary to simplify logic
            attributes['filterable'] = {}

        # We need to build our list of allowed HTTP methods
        if attributes.get('http_allowed_methods'):
            if not attributes.get('http_list_allowed_methods'):
                attributes['http_list_allowed_methods'] = \
                    attributes['http_allowed_methods']

            if not attributes.get('http_detail_allowed_methods'):
                attributes['http_detail_allowed_methods'] = \
                    attributes['http_allowed_methods']

        # We need to build our list of allowed methods
        if attributes.get('allowed_methods'):
            if not attributes.get('list_allowed_methods'):
                attributes['list_allowed_methods'] = \
                    attributes['allowed_methods']

            if not attributes.get('detail_allowed_methods'):
                attributes['detail_allowed_methods'] = \
                    attributes['allowed_methods']

        # Delegate to python to instantiate us.
        return super(Resource, cls).__new__(cls, name, bases, attributes)

    def __init__(self, name, bases, attributes):
        form = getattr(self, 'form', None)
        if form is not None:
            # Make a new fields list
            self.fields = OrderedDict()

            # A form as been declared; discover its fields
            self.discover_fields()

            # Instantiate anything that needs it
            # TODO: Cool to support 'x.y.z' notation here ?
            if self.filterer is not None:
                self.filterer = self.filterer()

        # Delegate to python to finish us up.
        super(Resource, self).__init__(name, bases, attributes)

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

    def __new__(meta, name, bases, attributes):
        # Ensure we have a valid model form.
        # First check if we have a model form.
        if attributes.get('form'):
            if not issubclass(attributes['form'], ModelForm):
                # Found a form; wasn't a model form -- tell the user to RTFM.
                raise ImproperlyConfigured('Use of a model resource requires '
                    "'form' to be a model form.")

            elif 'model' in attributes:
                # Let the user know this is unneccessary -- form overrides it
                warnings.warn("'model' is overriden by 'form'; "
                    "there is no need to declare 'model'.")

        elif 'model' in attributes:
            # Form wasn't declared; be nice and auto-generate a class
            # for them.
            class form(ModelForm):
                class Meta:
                    model = attributes['model']

            # Store the nicely generated one
            attributes['form'] = form

        # Delegate to python to instantiate us.
        return super(Model, meta).__new__(meta, name, bases, attributes)

    def discover_fields(self):
        # Discover explicitly declared fields first.
        super(Model, self).discover_fields()

        # Discover additional model fields.
        model = self.form._meta.model
        if model is not None:
            # Iterate through the list of fields using the provided form
            for field in model._meta.local_fields:
                name = field.name
                if self.is_field_visible(name):
                    # Grab the relation if there is one
                    relation = self.relations.get(name)
                    if not relation and isinstance(field, RelatedField):
                        # Field is a related model field but was not
                        # declared as a relation
                        continue

                    # Determine properties of the field and store it
                    self.fields[name] = fields.Model(
                            collection=isinstance(field, MultipleChoiceField),
                            relation=relation,
                            filterable=self.filterable.get(name)
                        )
