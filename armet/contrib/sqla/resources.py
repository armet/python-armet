import sqlalchemy as sa
from armet.resources.base import Resource, ResourceMeta
from armet.utils import classproperty, memoize
from sqlalchemy.orm import ColumnProperty, RelationshipProperty

# Mapping of 'Model' classes to canonical 'Resources'
_resources = {}

# Mapping of 'Tables' to 'Models'
_models = {}


class SQLAlchemyResourceMeta(ResourceMeta):

    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        if self._meta.model is not None:
            # Emplace ourself in the mapping for this model
            # TODO: We should be able to make a non-canonical resource
            _resources[self._meta.model] = self
            _models[self._meta.model.__table__] = self._meta.model

        if hasattr(self._meta, "attributes"):
            self.attributes = attrs = list(self._meta.attributes)

            # if self._meta.model is not None:
            #     # Cache the column set that will be fetched
            #     self._columns = []
            #     self._paths = []
            #     for name in attrs:
            #         path = name.split(".")
            #         attr = getattr(self._meta.model, path[0])
            #         if attr.impl is not None:
            #             if len(path) == 1 and attr.impl.accepts_scalar_loader:
            #                 # This is a scalar column and can be easily fetched
            #                 self._columns.append(attr)
            #
            #             else:
            #                 # This is a "relationship" attribute or path
            #                 # that is to be embedded
            #                 self._paths.append(path)


class SQLAlchemyResource(Resource, metaclass=SQLAlchemyResourceMeta):

    class Meta:
        # The model class object that this sqlalchemy resource will use.
        model = None

        # The session constructor used to build a session for this resource.
        session = None

        # Relationships to facilitate.
        relationships = []

    @classproperty
    @memoize
    def _paths(cls):
        paths = []
        for name in cls.attributes:
            path = name.split(".")
            attr = getattr(cls._meta.model, path[0])
            if len(path) > 1 or not isinstance(
                    attr.property, ColumnProperty):
                # This is /not/ a scalar column attribute
                paths.append(path)

        return paths

    @classproperty
    @memoize
    def _columns(cls):
        columns = []
        for name in cls.attributes:
            path = name.split(".")
            attr = getattr(cls._meta.model, path[0])
            if len(path) == 1 and isinstance(attr.property, ColumnProperty):
                # This is a scalar column and can be easily fetched
                columns.append(attr)

        return columns

    def read(self):
        # Build the base queryset (over each scalar column)
        queryset = self._meta.session().query(*self._columns)

        # Iterate each `path`
        entities = []
        for path in self._paths:
            # Build the selectable for the end-result and join the
            # neccessary table(s) to get there
            selectable = None
            entity = True
            for segment in path:
                attr = getattr(self._meta.model, segment)

                # Get the `target_table` and `target` and make that
                # the selectable
                target_table = attr.property.target
                target = _models[target_table]
                selectable = target

                # Join the table to us in our quest to get this attribute
                queryset = queryset.outerjoin(target, attr.expression)

            if entity:
                queryset = queryset.add_entity(selectable)

        return queryset

    def filter(self, queryset, query):
        # Apply the slug to the queryset
        if self.slug is not None:
            slug_column = getattr(
                self._meta.model, self._meta.slug_attribute)
            queryset = queryset.filter(slug_column == self.slug)


        return queryset

    @classmethod
    def prepare_item(cls, item):
        # Prepare the initial (scalar) dataset
        data = super().prepare_item(item)

        # Iterate through our relationships (and prepare and embed)
        # cnt = len(cls._columns)
        # for idx, path in enumerate(cls._paths):
        # data[path[-1]] = item[cnt + idx]
        # attr = getattr(cls._meta.model, key)
        # target_table = attr.property.target
        # target = _models[target_table]
        # resource = _resources[target]
        # value = getattr(item, target.__name__, None)
        # if value is not None:
        #     data[key] = resource.prepare_item(value)

        return data
