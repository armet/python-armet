from ._version import __version__
from . import encoders, decoders, codecs

__all__ = [
    __version__,
    encoders,
    decoders
]


# Register each encoder.
encoders.register(encoders.URLEncoder.encode,
                  names=codecs.URLCodec.names,
                  mime_types=codecs.URLCodec.mime_types)

# Register each decoder.
decoders.register(decoders.URLDecoder.decode,
                  names=codecs.URLCodec.names,
                  mime_types=codecs.URLCodec.mime_types)
