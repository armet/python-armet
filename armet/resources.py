

# Registry of preparation functions (by name and type)
_prepares = {}

# Registry of cleaning functions (by name and type)
_cleans = {}


class Resource:

    # Set of named attributes to faclitiate from the `item` returned
    # from the `read` method.
    attributes = set()

    def __init__(self, slug=None, context=None):
        """
        :param slug: Identifier that represents which item of the resource
                     to return, if present.
        :type context: str or None

        :param context: Context in which this resource is being called (eg.
                        a nested resource will receive the result of a `read`
                        from the parent resource in its context).
        :type context: dict or None
        """
        self.slug = slug
        self.context = context or {}

    def prepare_item(self, item):
        data = {}
        for name in self.attributes:
            try:
                value = getattr(item, name)

            except AttributeError:
                continue

            # Attempt to use a preparation function, by name.
            name_prepare = _prepares.get(name)
            if name_prepare:
                value = name_prepare(item, name, value)

            data[name] = value

        return data

    def prepare(self, items):
        data = [self.prepare_item(item) for item in items]

        if self.slug is None:
            return data

        try:
            return data[0]

        except IndexError:
            raise exceptions.NotFound


def prepares(*clauses):
    """
    Registers a preparation function to be invoked for each clause in
    the decorator.

    A preparation clause is invoked on each attribute after it is retrieved
    from the item returned from the `read` function.

    A clause may be a string or a type. If it is a string then the clause
    describes an attribute of a resource by name. If it is a type then the
    clause would be applied to all attributes of that type (or are an instance
    of that type).

    A preparation function may be "scoped" to a specific resource
    by decorating a method (instead of a module function).

    ::
        @prepares(datetime.datetime)
        def prepare_datetime(item, key, value):
            return value.isoformat()

        @prepares("id")
        def prepare_id(item, key, value):
            return str(value)

        class User(Resource):

            @prepares("id")
            def prepare_id(self, item, key, value):
                return value.hex
    """
    def decorator(fn):
        # Register this preparation function for each passed clause.
        for clause in clauses:
            _prepares[clause] = fn

        # Return the original function.
        return fn

    return decorator


def cleans(*clauses):
    """
    Registers a cleaning function to be invoked for each clause in
    the decorator.

    A cleaning clause is invoked on each attribute after it is received
    from the decoder and before it is sent to the `update` or `create`
    functions.

    Otherwise the semantics are equivalent to the `prepares` decorator.

    ::
        @cleans(datetime.datetime)
        def clean_datetime(key, value):
            from dateutil import parse
            return parse(value)

        @cleans("id")
        def clean_id(key, value):
            return UUID(value)

        class User(Resource):

            @cleans("id")
            def clean_id(self, key, value):
                return UUID(value)
    """
