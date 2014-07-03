import mimeparse


class CodecRegistry:
    """A registry used for registering and removing encoders and decoders.
    """

    def __init__(self):
        self._codecs = {}
        self._mime_types = {}

    def find(self, *, media_range=None, name=None, mime_type=None):
        """
        Attempt to find a compliant codec given either a mime_type or
        codec name.  Prioritize the mime-type, then name, then media_range.
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

    def register(self, codec, names=(), mime_types=()):
        """Register the transcoder provided in the global list of transcoders.
        """

        self._codecs.update({x: codec for x in names})
        self._mime_types.update({x: codec for x in mime_types})

    def remove(self, codec=None, *, name=None, mime_type=None):
        """Remove the codec from the global list of available codecs.

        Attempts to match the codec by name or mime_type if passed (but
        prioritizes codec if passed).
        """

        if codec is not None:
            for registry in (self._codecs, self._mime_types):
                for name, test in list(registry.items()):
                    if codec is test:
                        del registry[name]

        if name is not None:
            self.remove(self._codecs.get(name))

        if mime_type is not None:
            self.remove(self._mime_types.get(mime_type))


class URLCodec:

    preferred_mime_type = 'application/x-www-form-urlencoded'

    mime_types = {preferred_mime_type}

    names = {'url'}


class JSONCodec:

    preferred_mime_type = 'application/json'

    mime_types = {
        preferred_mime_type,
        # Offical; as per RFC 4627.
        'application/json',

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
