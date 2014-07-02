import mimeparse


class CodecRegistry:
    """A registry used for registering and removing encoders and decoders.
    """

    def __init__(self):
        self._encoders = {}
        self._mime_types = {}

    def find(self, *, media_range=None, name=None, mime_type=None):
        """
        Attempt to find a compliant encoder given either a mime_type or
        encoder name.  Prioritize the mime-type, then name, then media_range.
        """

        if mime_type is not None:
            return self._mime_types[mime_type]

        if name is not None:
            return self._encoders[name]

        if media_range is not None:
            return self._find_media_range(media_range)

        raise TypeError(
            'At least one parameter is required: '
            'media_range, mime_type, or name.')

    def _find_media_range(self, media_range):
        try:
            found = mimeparse.best_match(self._mime_types.keys(), media_range)

        except ValueError:
            raise KeyError('Malformed media range.')

        if found is None:
            raise KeyError

        return self._mime_types[found]

    def register(self, encoder, names=(), mime_types=()):
        """Register the transcoder provided in the global list of transcoders.
        """

        self._encoders.update({x: encoder for x in names})
        self._mime_types.update({x: encoder for x in mime_types})

    def remove(self, encoder):
        """Remove the encoder from the global list of available encoders.
        """

        for registry in (self._encoders, self._mime_types):
            for name, test in list(registry.items()):
                if encoder is test:
                    del registry[name]
