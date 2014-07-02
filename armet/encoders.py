from .codecs import CodecRegistry


# Create our encoder registry and pull methods off it for easy access.
_registry = CodecRegistry()

find = _registry.find
remove = _registry.remove
register = _registry.register
