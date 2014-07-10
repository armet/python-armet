import mimeparse
from collections import Iterable
from .registry import Registry


# class Codec:
#
#     """A wrapper for a codec entered into the CodecRegistry.
#     """
#
#     def __init__(self, fn, names, mime_types):
#         self.transcode = fn
#         self.names = names
#         self.mime_types = mime_types
#
#     def __call__(self, *args, **kwargs):
#         return self.transcode(*args, **kwargs)
#
#     def __eq__(self, other):
#         try:
#             # Compare our contained function with the passed function or
#             # the passed container's function.
#             return (self.transcode == other or
#                     self.transcode == other.transcode)
#
#         except AttributeError:
#             return NotImplemented


class CodecRegistry(Registry):
    """A registry used for registering and removing encoders and decoders.
    """

    # def __init__(self):#, Wrapper=Codec):
        # super().__init__()

        # Codec wrapper constructor. Returns a wrapped version of the codec
        # Invoking the wrapper should invoke the codec.
        # self._Wrapper = Wrapper

    def find_media_range(self, media_range):
        try:
            # best_match returns empty string on failure to find a match.
            # The correct KeyError will be thrown when attempting the lookup
            # below.
            found = mimeparse.best_match(self.map["mime_type"].keys(),
                                         media_range)

        except ValueError:
            raise KeyError('Malformed media range.')

        # Push the resolved mime_type into the `find` method.
        return self.find(mime_type=found)

    # def _register(self, codec_fn, names=(), mime_types=(), **kwargs):
    #     """Register the transcoder provided in the global list of transcoders.
    #     """
    #
    #     # Sanity check.
    #     assert len(names) or len(mime_types), (
    #         "Encoder/Decoder cannot be registered without at least one of "
    #         "'names' or 'mime_types'")
    #
    #     codec = self._Wrapper(codec_fn, names, mime_types, **kwargs)
    #
    #     self._codecs.update({x: codec for x in names})
    #     self._mime_types.update({x: codec for x in mime_types})


class URLCodec:

    preferred_mime_type = 'application/x-www-form-urlencoded'

    mime_types = {preferred_mime_type}

    names = {'url'}


class JSONCodec:

    # Offical; as per RFC 4627.
    preferred_mime_type = 'application/json'

    mime_types = {
        preferred_mime_type,

        # Widely used (thanks <http://www.json.org/JSONRequest.html>.)
        'application/jsonrequest',

        # Miscellaneous mimetypes that are used frequently (incorrectly).
        'application/x-json',
        'text/json',

        # Widely used (incorrectly) thanks to ruby.
        'text/x-json',
    }

    names = {'json'}


class FormDataCodec:

    preferred_mime_type = 'multipart/form-data'

    mime_types = {preferred_mime_type}

    names = {'form'}
