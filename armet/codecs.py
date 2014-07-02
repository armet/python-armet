import mimeparse


def register_module(module, base):
    """Used to register all the codecs in a module.
    Invoke using the module and the base class to test inheritance against."""
    for name in dir(module):
        d = getattr(module, name)
        if isinstance(d, type) and issubclass(d, base) and d is not base:
            module.register(d, names=d.names, mime_types=d.mime_types)


class CodecRegistry:
    """A registry used for registering and removing encoders and decoders.
    """

    def __init__(self):
        self._codecs = {}
        self._mime_types = {}

    def find(self, *, media_range=None, name=None, mime_type=None):
        """
        Attempt to find a compliant encoder given either a mime_type or
        encoder name.  Prioritize the mime-type, then name, then media_range.
        """

        if mime_type is not None:
            return self._mime_types[mime_type]

        if name is not None:
            return self._codecs[name]

        if media_range is not None:
            return self._find_media_range(media_range)

        raise TypeError(
            'At least one parameter is required: '
            'media_range, mime_type, or name.')

    def _find_media_range(self, media_range):
        try:
            # best_match returns empty string on failure to find a match.
            # The correct KeyError will be thrown when attempting the lookup
            # below.
            found = mimeparse.best_match(self._mime_types.keys(), media_range)

        except ValueError:
            raise KeyError('Malformed media range.')

        return self._mime_types[found]

    def register(self, encoder, names=(), mime_types=()):
        """Register the transcoder provided in the global list of transcoders.
        """

        self._codecs.update({x: encoder for x in names})
        self._mime_types.update({x: encoder for x in mime_types})

    def remove(self, encoder=None, name=None, mime_type=None):
        """Remove the encoder from the global list of available encoders.

        Attempts to match the encoder by name or mime_type if passed (but
        prioritizes encoder if passed).
        """

        if encoder is not None:
            for registry in (self._codecs, self._mime_types):
                for name, test in list(registry.items()):
                    if encoder is test:
                        del registry[name]

            return

        elif name is not None:
            encoder = self._codecs.get(name)

        elif mime_type is not None:
            encoder = self._mime_types.get(mime_type)

        if encoder is not None:
            self.remove(encoder)


class Codec:
    """Generic base class for all Codec data.  This is a common class used
    for both the encoder and decoder."""

    # The preferred mime-type for this encoder.  This is reported in the
    # Content-Type header when sending data to the client
    preferred_mime_type = ''

    # The mime-types that this encoder can work with, in no particular order.
    mime_types = set()

    # The common names that this encoder is known by.  This is used to
    # determine encoders chosen based on file extension (/api/foo.json)
    names = set()


class URLCodec(Codec):

    preferred_mime_type = 'application/x-www-form-urlencoded'

    mime_types = {
        preferred_mime_type}

    names = {
        'url',
        'urlencoded'}
