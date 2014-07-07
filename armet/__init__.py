from ._version import __version__
from . import encoders, decoders, codecs

__all__ = [
    __version__,
    encoders,
    decoders
]


# # Register each encoder.
# # URL Encoder
# encoders.register(encoders.URLEncoder.encode,
#                   names=codecs.URLCodec.names,
#                   mime_types=codecs.URLCodec.mime_types)

# # JSON Encoder
# encoders.register(encoders.JSONEncoder.encode,
#                   names=codecs.JSONCodec.names,
#                   mime_types=codecs.JSONCodec.mime_types)

# # FormData encoder
# encoders.register(encoders.FormEncoder,
#                   names=codecs.FormDataCodec.names,
#                   mime_types=codecs.FormDataCodec.mime_types)

# # Register each decoder.
# # URL Decoder
# decoders.register(decoders.URLDecoder.decode,
#                   names=codecs.URLCodec.names,
#                   mime_types=codecs.URLCodec.mime_types)

# # JSON Decoder
# decoders.register(decoders.JSONDecoder.decode,
#                   names=codecs.JSONCodec.names,
#                   mime_types=codecs.JSONCodec.mime_types)

# # Form Decoder
# decoders.register(decoders.FormDecoder.decode,
#                   names=codecs.FormDataCodec.names,
#                   mime_types=codecs.FormDataCodec.mime_types)
