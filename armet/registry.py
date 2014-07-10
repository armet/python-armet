from collections import defaultdict


class Registry:

    def __init__(self):
        self.map = defaultdict(dict)

    def register(self, obj=None, **kwargs):

        def callback(obj):
            if obj is None:
                raise TypeError("'%s' object cannot be registered" %
                                type(obj).__name__)

            for key, value in kwargs.items():
                self.map[key][value] = obj

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
            return lookup(value)

        except KeyError:
            # If we don't find what they were looking for; return nothing.
            return None

    def remove(self, *args, **kwargs):
        # For each passed object we need to iterate through each nested
        # dictionary and remove each reference to it.
        for obj in args:
            for registry_name, registry in list(self.map.items()):
                for name, item in list(registry.items()):
                    if item is obj:
                        del registry[name]

                if not registry:
                    del self.map[registry_name]

        # For each passed reference we retrieve the object at the reference
        # and recurse into removing every reference for that object.
        for key, value in kwargs.items():
            try:
                self.remove(self.map[key][value])

            except IndexError:
                pass
