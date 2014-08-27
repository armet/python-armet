from .registry import _prepare
import collections


class ResourceMeta(type):

    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        # Collect `Meta` information and store on `_meta`
        # This aggregates all base class `Meta` information
        metadata = {}

        for base in bases:
            _meta = getattr(base, "_meta", None)
            if _meta is None:
                _meta = {}
            else:
                _meta = vars(_meta)
            metadata.update(_meta)

        meta = attrs.get("Meta")
        if meta:
            for name, value in vars(meta).items():
                if not name.startswith("_"):
                    metadata[name] = value

        # Create and store the metadata as `_meta`
        self._meta = type("Meta", (), metadata)


class Resource(metaclass=ResourceMeta):

    class Meta:
        # Set of named attributes to faclitiate from the `item` returned
        # from the `read` method.
        attributes = set()
        relationships = set()

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

    @classmethod
    def prepare_item(cls, item):
        # data = {}
        data = collections.OrderedDict()
        for name in cls.attributes:
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

    def filter(self, items, query):
        # TODO: Apply `slug` filtering
        # TODO: Apply `context` filtering
        # TODO: Apply `query` filtering
        return query

    def prepare(self, items):
        return [self.prepare_item(item) for item in items]
