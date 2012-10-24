""" ..
"""


class Field(object):
    # ..
    def __init__(self, name, **kwargs):
        #! Name of the field on the object instance.
        self.name = name

        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)


class Related(Field):
    # ..
    def __init__(self, name, relation, **kwargs):
        #! Resource in relation to this.
        self.relation = relation
        super(Related, self).__init__(name, **kwargs)
