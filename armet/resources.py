
# NOTE: Should this be that `Registry` thing we were talking about?
_registry = {}


def resource(handler=None, **kwargs):

    def decorator(handler):
        # Register the handler according to the name.
        name = kwargs.get("name") or handler.__name__.lower()
        if isinstance(handler, type):
            _registry[name] = handler

        else:
            _registry[name] = type(name, (), {
                "route": lambda self, request: handler(request)
            })

        # Return the original function, unmodified.
        return handler

    if handler is None:
        return decorator

    return decorator(handler)
