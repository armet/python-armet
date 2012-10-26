""" ..
"""


class Field(object):
    # ..
    def __init__(self, **kwargs):
        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)

        #! Resource in relation to this.
        self.relation = kwargs.get('relation')


class Model(Field):
    # ..
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)
