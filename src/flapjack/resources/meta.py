from collections import OrderedDict
from django.utils.functional import cached_property
from django.forms import ModelForm, MultipleChoiceField
from django.db.models import ForeignKey, ManyToManyField
from . import fields


class Resource(type):

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
        cls._fields = OrderedDict()

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
        super(Resource, cls).__init__(name, bases, attributes)


class Model(Resource):

    def __init__(cls, name, bases, attributes):
        # Delegate to more magic to initialize the class object
        super(Model, cls).__init__(name, bases, attributes)

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
