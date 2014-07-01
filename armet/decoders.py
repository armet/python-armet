from .transcoders import TranscoderRegistry


# Create our encoder registry and pull methods off it for easy access.
registry = TranscoderRegistry()

find = registry.find
purge = registry.purge
register = registry.register
