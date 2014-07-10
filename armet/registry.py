from collections import defaultdict


class Registry:

    def __init__(self):
        self._registry = defaultdict(dict)

    def register(self, obj, **kwargs):
        if obj is None:
            raise TypeError("'%s' object cannot be registered" %
                            type(obj).__name__)

        for key, value in kwargs.items():
            self._registry[key][value] = obj

    def find(self, **kwargs):
        if len(kwargs) > 1:
            raise TypeError(
                "%s.find expected at most 1 keyword argument, got %d" % (
                    type(self).__name__, len(kwargs)))

        try:
            key, value = kwargs.popitem()
            return self._registry[key][value]

        except KeyError:
            # If we don't find what they were looking for; return nothing.
            return None

    def remove(self, *args, **kwargs):
        # For each passed object we need to iterate through each nested
        # dictionary and remove each reference to it.
        for obj in args:
            for registry_name, registry in list(self._registry.items()):
                for name, item in list(registry.items()):
                    if item is obj:
                        del registry[name]

                if not registry:
                    del self._registry[registry_name]

        # For each passed reference we retrieve the object at the reference
        # and recurse into removing every reference for that object.
        for key, value in kwargs.items():
            try:
                self.remove(self._registry[key][value])

            except IndexError:
                pass
