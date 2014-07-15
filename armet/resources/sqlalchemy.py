from .base import Resource


class SQLAlchemyResource(Resource):

    # The model class object that this sqlalchemy resource will use.
    model = None

    # The session constructor used to build a session for this resource.
    session = None

    def __new__(cls):
        # This behaves as a hook to assert the set of attributes is ordered
        # and begins with the slug attribute

        # TODO: this is executed every time an instance is constructed.
        # move this to some kind of metaclass or metaclass hook.
        attrs = set(cls.attributes)
        attrs.discard(cls.slug_attribute)
        cls.attributes = [cls.slug_attribute] + list(attrs)

    def read(self):
        """Return a sqlalchemy query object of columns."""
        columns = (getattr(self.model, name) for name in self.attributes)
        return self.session().query(*columns)

    def filter(self, saquery, armetquery):
        """Filter hook!  Used to filter the slug and any armet queries."""

        # Filter by the slug.
        if self.slug is not None:
            saquery = saquery.filter_by(**{self.slug_attribute: self.slug})

        # TODO: Armet query filtering.
        return saquery

    def prepare(self, items):
        # Turn models into dictionaries!
        return [zip(self.attributes, x) for x in items]

    def prepare_item(self, item):
        return zip(self.attributes, item)
