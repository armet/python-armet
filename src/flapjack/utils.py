import functools


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, cls):
        return self.getter(cls)


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer


def flatten_parameters(params):
    """Flattens a dict where each value is a list of 1 or more things into a
    dict where each value is either an object or a list of 2 or more things
    """
    for k, v in params.items():
        if len(v) == 1:
            params[k] = v[0]
    return params
