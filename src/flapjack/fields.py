from . import utils
from django.db.models.fields import NOT_PROVIDED


class Field(object):

    def __init__(self, **kwargs):
        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)

        #! Whether this field may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! Visibility of the field.
        self.visible = kwargs.get('visible', False)

        #! Default value for the field.
        self.default = kwargs.get('default')

        #! Whether this fields is bound to a model or not.
        self.model = kwargs.get('model', False)

        #! Accessor function that will get the value of the field from the obj.
        self.accessor = kwargs.get('accessor')

        #! Preparation function that is linked to the class object of the
        #! instantiating resource.
        self.prepare = kwargs.get('prepare')
        if self.prepare is None:
            self.prepare = lambda s, o, v: v

    def clean(self, value):
        """Cleans the value for consumption by the form clean cycle."""
        # Base field class just passes the value through.
        return value


class BooleanField(Field):

    #! Values accepted for `True`.
    TRUE = (
        'true',
        't',
        'yes',
        'y',
        'on'
        '1'
    )

    #! Values accepted for `False`.
    FALSE = (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    )

    def clean(self, value):
        if value.strip().lower() in self.TRUE:
            # Some sort of truthy value.
            return True

        if value.strip().lower() in self.FALSE:
            # Some sort of falsy value.
            return False

        # Neither true or false matches; return what we were given.
        return value


class DateField(Field):
    pass


class TimeField(Field):
    pass


class DateTimeField(Field):
    pass


class FileField(Field):
    pass
