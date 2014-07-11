from ..codecs import CodecRegistry


__all__ = [
    "find",
    "remove",
    "register"
]


# Construct a module-scoped registry for the decoders.
_registry = CodecRegistry()

# Take the general methods and attach to the module for easy access.
find = _registry.find
remove = _registry.remove
register = _registry.register


# Import the builtin decoders (which can be overriden by a user).
from . import json, url, form  # noqa
