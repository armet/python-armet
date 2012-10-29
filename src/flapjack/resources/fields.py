""" ..
"""


class Field(object):
    def __init__(self, name, **kwargs):
        #! Name of the field on the object or dictionary.
        self.name = name

        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)

        #! Resource object in relation to this.
        self.relation = kwargs.get('relation')

        #! Whether this field may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! The underlying python type of this field.
        self.type = kwargs.get('type', str)

        #! A function to sanitize a string to the presented python type.
        self.clean = kwargs.get('clean', lambda x: x)

        #self.direct = kwargs.get('direct', True)
        #self.hidden = kwargs.get('hidden', False)
        #self.parse = kwargs.get('parse')


class Model(Field):
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)
