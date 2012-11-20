from . import utils
from django.db.models.fields import NOT_PROVIDED


class Field(object):

    def __init__(self, name, **kwargs):
        #! Name of the field on the object or dictionary.
        self.name = name

        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.iterable = kwargs.get('iterable', False)

        #! Whether this field may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! Visibility of the field.
        self.visible = kwargs.get('visible', False)

        #! Default value for the field.
        self.default = kwargs.get('default')

        #! Whether this fields is bound to a model or not.
        self.model = kwargs.get('model')

    def clean(self, value):
        """Prepares the value for consumption by the form clean cycle."""
        # Base field class just passes the value through.
        return value


class BooleanField(Field):

    # #! Values for
    # TRUE = (
    # )

    # def clean(self, value):
    #     if value.strip().lower() in ('true', 't'):
    #         return


class DateField(Field):
    pass


class TimeField(Field):
    pass


class DateTimeField(Field):
    pass


class FileField(Field):
    pass
