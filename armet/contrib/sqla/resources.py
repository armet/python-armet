from armet.resources import Resource


class SQLAlchemyResource(Resource):

    # The model class object that this sqlalchemy resource will use.
    model = None

    # The session constructor used to build a session for this resource.
    session = None

    # Relationships to facilitate.
    # NOTE: Should be a dictionary of names to models (for now)
    # FIXME: Should be able to "look up the model"
    relationships = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This behaves as a hook to assert the set of attributes is ordered
        # and begins with the slug attribute

        # FIXME: The slug_attribute shouldn't need to be an actual attribute

        # TODO: this is executed every time an instance is constructed.
        # move this to some kind of metaclass or metaclass hook.
        attrs = set(self.attributes)
        attrs.discard(self.slug_attribute)
        self.attributes = [self.slug_attribute] + list(attrs)

    def read(self):
        # TODO: Column set could be cached
        columns = (getattr(self.model, name) for name in self.attributes)
        return self.session().query(*columns)

    def filter(self, queryset, query):
        # Apply the slug to the queryset
        if self.slug is not None:
            # TODO: Slug column could be cached
            slug_column = getattr(self.model, self.slug_attribute)
            queryset = queryset.filter(slug_column == self.slug)

        # Apply the relationship context to the queryset
        for name, relation in self.relationships.items():
            if name in self.context:
                queryset = queryset.join(relation).filter(
                    self.context[name].whereclause)

                del self.context[name]

        return queryset
