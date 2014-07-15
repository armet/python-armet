from .registry import _prepare


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
                # Attempt to get the attribute from the item.
                value = getattr(item, name)

                # Run the value through the preparation cycle.
                value = _prepare(item, name, value)

            except AttributeError:
                # Item does not have the attribute; just put `None`
                # in the object.
                value = None
                continue

            data[name] = value

        return data

    def prepare(self, items):
        return [self.prepare_item(item) for item in items]
