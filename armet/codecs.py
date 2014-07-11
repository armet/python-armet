import mimeparse
from .registry import Registry


class CodecRegistry(Registry):
    """A registry used for registering and removing encoders and decoders.
    """

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
