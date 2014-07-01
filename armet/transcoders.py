import mimeparse


class TranscoderRegistry:
    """A registry used for registering and removing encoders and decoders.
    """
    def __init__(self):
        self.encoders = {}
        self.mime_types = {}

    def find(self, *, media_range=None, name=None, mime_type=None):
        # Attempt to find a compliant encoder given eitehr a mime_type or
        # encoder name.  Prioritize the mime-type, then name, then media_range.

        if mime_type is not None:
            return self.mime_types[mime_type]
        elif name is not None:
            return self.encoders[name]
        elif media_range is not None:
            return self.find_media_range(media_range)

        raise TypeError(
            'At least one parameter is required: '
            'media_range, mime_type, name.')

    def find_media_range(self, media_range):
        try:
            found = mimeparse.best_match(self.mime_types.keys(), media_range)

        except ValueError:
            raise TypeError('Malformed media range.')

        if found is None:
            raise KeyError

        return self.mime_types[found]

    def register(self, encoder, names=[], mime_types=[]):
        # Register the transcoder provided in the global list of
        # transcoders.

        self.encoders.update({x: encoder for x in names})
        self.mime_types.update({x: encoder for x in mime_types})

    def purge(self, encoder):
        # Remove the encoder from the global list of available encoders.
        for registry in (self.encoders, self.mime_types):
            collection = set()
            for name, test in registry.items():
                if encoder is test:
                    collection.add(name)

            # Need to apply the deletions after iterating over the registry
            # otherwise an exception is thrown because the dictionary changed
            # size during iteration.
            for key in collection:
                del registry[key]
