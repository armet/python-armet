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

        self.direct = kwargs.get('direct', True)
        self.hidden = kwargs.get('hidden', False)
        self.name = kwargs.get('name', None)  # Need this really
        self.related_name = kwargs.get('related_name', self.name)
        self.parse = kwargs.get('parse')


class Model(Field):
    # ..
    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)
