from collections import defaultdict, Iterable


class Registry:

    def __init__(self, fallback=None, index=None):
        """Generic registry for easy lookup.

        If the item is not found, on find() And a "fallback" registry is
        provided, the item requested will be searched through the fallback
        registry.
        """
        self.map = defaultdict(dict)
        self.fallback = fallback
        self.index = index
        self.metadata = {}

    def register(self, obj=None, **kwargs):

        def callback(obj):
            if obj is None:
                raise TypeError("'%s' object cannot be registered" %
                                type(obj).__name__)

            metadata = {}
            for key, value in kwargs.items():
                if isinstance(value, Iterable) and not isinstance(value, str):
                    metadata[key] = []
                    for val in value:
                        metadata[key].append(val)
                        if self.index is None or key in self.index:
                            self.map[key][val] = obj

                else:
                    metadata[key] = value
                    if self.index is None or key in self.index:
                        self.map[key][value] = obj

            self.metadata[obj] = metadata

            return obj

        if obj is None:
            # If no object was passed in we assume the user is attempting
            # to use this as a decorator.
            return callback

        # Just invoke the callback directly
        callback(obj)

    def find(self, **kwargs):
        if len(kwargs) > 1:
            raise TypeError(
                "%s.find expected at most 1 keyword argument, got %d" % (
                    type(self).__name__, len(kwargs)))

        try:
            # Pop the (key, value) pair to pass to the lookup method.
            key, value = kwargs.popitem()

            # Resolve a `find_FOO` method.
            # The idea here is that a derived class could define
            # a custom lookup method for a specific attribute.
            lookup = getattr(self, "find_%s" % key,
                             lambda v: self.map[key][v])

            # Utilize the lookup method to attempt to find the object
            # by the passed value.
            obj = lookup(value)
            return obj, self.metadata[obj]

        except KeyError:
            if self.fallback is not None:
                # If we don't find what they were looking for; return nothing.
                return self.fallback.find(**{key: value})

            # Re-raise the key-error
            raise

    def remove(self, *args, **kwargs):
        # For each passed object we need to iterate through each nested
        # dictionary and remove each reference to it.
        for obj in args:
            for registry_name, registry in list(self.map.items()):
                for name, item in list(registry.items()):
                    if item == obj:
                        del registry[name]

                if not registry:
                    del self.map[registry_name]

        # For each passed reference we retrieve the object at the reference
        # and recurse into removing every reference for that object.
        for key, value in kwargs.items():
            try:
                self.remove(self.map[key][value])

            except KeyError:
                pass
