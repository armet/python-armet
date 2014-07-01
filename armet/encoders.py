from .transcoders import TranscoderRegistry


# Create our encoder registry and pull methods off it for easy access.
registry = TranscoderRegistry()

find = registry.find
purge = registry.purge
register = registry.register


class Encoder:
    """Base class for all encoders."""

    def encode(self, data):
        """Entrypoint for logic used to encode an entire block.
        If a type is not encodable, a TypeError may be raised."""
        raise NotImplementedError
