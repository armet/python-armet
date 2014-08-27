import sqlalchemy as sa
from armet.resources.base import Resource, ResourceMeta
from armet.utils import classproperty, memoize
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.ext.associationproxy import AssociationProxy

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
    def _segment_attributes(cls):
        columns = []
        rels = []
        calculated = []
        for name in cls.attributes:
            attr = getattr(cls._meta.model, name)
            if (hasattr(attr, "property")
                    and isinstance(attr.property, ColumnProperty)):
                # This is a scalar column and can be easily fetched
                columns.append(attr)
            elif (hasattr(attr, "property")
                    and isinstance(attr.property, MapperProperty)):
                # This is /not/ a scalar column attribute
                # but is stil sqlalchemy-y
                rels.append(name)
            else:
                calculated.append(name)

        return columns, rels, calculated

    @classproperty
    def _calculated(cls):
        return cls._segment_attributes[2]

    @classproperty
    def _relationships(cls):
        return cls._segment_attributes[1]

    @classproperty
    def _columns(cls):
        return cls._segmented_attributes[0]

    def read(self):
        # Build the base queryset (over each scalar column)
        queryset = self._meta.session().query(self._meta.model)

        # Iterate each `relationship`
        entities = []
        for rel in self._relationships:
            # Build the selectable for the end-result and join the
            # neccessary table(s) to get there
            attr = getattr(self._meta.model, rel)
            direction = attr.property.direction.name
            if direction == "MANYTOONE":
                # Get the `target_table` and `target` and make that
                # the selectable
                target_table = attr.property.target
                target = _models[target_table]

                # Join the table to us in our quest to get this attribute
                queryset = queryset.outerjoin(target, attr.expression)

            else:
                # TO-MANY attributes are added later
                continue

            # Add the 'enttiy' to the queryset
            queryset = queryset.add_entity(target)

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
        # If we didn't get a (tuple,) ...
        if not isinstance(item, tuple):
            item = (item,)

        # Check to see if we need to polymorphically
        # apply a different resource
        if type(item[0]) is not cls._meta.model:
            resource = _resources.get(type(item[0]))
            if resource is not None:
                return resource.prepare_item(item)

        # Prepare the initial (scalar) dataset
        data = super().prepare_item(item[0])

        # Iterate through our relationships (and prepare and embed)
        for idx, rel in enumerate(cls._relationships):

            # FIXME: This could be calculated in `read`
            attr = getattr(cls._meta.model, rel)
            direction = attr.property.direction.name
            target_table = attr.property.target
            target = _models[target_table]

            resource = _resources[target]

            if direction == "MANYTOONE":
                # Get the value and prepare it appropriately
                value = item[1 + idx]

                if value is not None:
                    cls._set_item(data, rel, resource.prepare_item(value))

                else:
                    cls._set_item(data, rel, None)

            elif direction == "ONETOMANY":
                # Get the values
                values = getattr(item[0], rel)

                # Prepare each value and add to the data
                cls._set_item(data, rel, resource.prepare(values))

        # Apply calculated attributes
        for name in cls._calculated:
            cls._set_item(data, name, getattr(item[0], name))

        return data
