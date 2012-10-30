from . import utils
from django.db.models.fields import NOT_PROVIDED


class Field(object):

    @property
    @utils.memoize
    def relation(self):
        if 'relation_name' in self.__dict__:
            segments = self.relation_name.split('.')
            module = '.'.join(segments[:-1])
            m = __import__(module)
            for segment in segments[1:]:
                m = getattr(m, segment)
            return m

        else:
            return None

    def __init__(self, name, **kwargs):
        #! Name of the field on the object or dictionary.
        self.name = name

        #! Whether this field can be modified or not.
        self.editable = kwargs.get('editable', False)

        #! Whether this field is a collection or not.
        self.collection = kwargs.get('collection', False)

        relation = kwargs.get('relation')
        if isinstance(relation, type):
            #! Resource object in relation to this.
            self.relation = relation

        elif relation:
            #! Resource relation name to lazy load later.
            self.relation_name = relation

        #! Whether this field may be filtered or not.
        self.filterable = kwargs.get('filterable', False)

        #! A function to sanitize a string to the presented python type.
        self.clean = kwargs.get('clean', lambda x: x)

        #! Visibility of the field.
        self.visible = kwargs.get('visible', False)

        #! Default value for the field.
        default = kwargs.get('default')
        self.default = default if default is not NOT_PROVIDED else None

        #! Whether this field expects to be a file.
        self.file = kwargs.get('file', False)


class Model(Field):
    def __init__(self, name, **kwargs):
        super(Model, self).__init__(name, **kwargs)
