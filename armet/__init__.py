from ._version import __version__
from . import encoders, decoders, codecs  # flake8: noqa


# Register all modules in encoders and decoders
codecs.register_module(encoders, encoders.Encoder)
codecs.register_module(decoders, decoders.Decoder)
