from collections import Iterable, Mapping, OrderedDict


class CycleRegistry(dict):

    def __init__(self, fallback=None):
        super().__init__()

        # A fallback dictionary to use if the key is not in this dictionary.
        self._fallback = fallback

    def __missing__(self, key):
        # If the key is a "type" we should attempt to iterate back through
        # its MRO to resolve it based on inheritance.
        if isinstance(key, type):
            for cls in key.__mro__:
                if cls in self:
                    # Cache this for the next lookup.
                    self[key] = self[cls]

                    # Return the result.
                    return self[cls]

        # If we have a fallback dictionary, use that.
        if self._fallback:
            return self._fallback[key]

        # Raise a KeyError as we don't have this.
        raise KeyError


# Registry of preparation functions (by name and type)
_prepares = CycleRegistry()

# Registry of cleaning functions (by name and type)
_cleans = CycleRegistry()


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
        # data = OrderedDict()
        data = {}
        for name in self.attributes:
            try:
                # Attempt to get the attribute from the item.
                value = getattr(item, name)

            except AttributeError:
                # Item does not have the attribute; just put `None`
                # in the object.
                data[name] = None
                continue

            try:
                # Attempt to get a preparation function, by type.
                prepare = _prepares[type(value)]

            except KeyError:
                try:
                    # Attempt to get a preparation function, by name.
                    prepare = _prepares[name]

                except KeyError:
                    # No preparation function; continue.
                    data[name] = value
                    continue

            # Prepare and push the attribute in the object.
            data[name] = prepare(item, name, value)

        return data

    def prepare(self, items):
        return [self.prepare_item(item) for item in items]


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
    def decorator(function):
        # Register this preparation function for each passed clause.
        for clause in clauses:
            _prepares[clause] = function

        # Return the original function.
        return function

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
    def decorator(function):
        # Register this preparation function for each passed clause.
        for clause in clauses:
            _cleans[clause] = function

        # Return the original function.
        return function

    return decorator
