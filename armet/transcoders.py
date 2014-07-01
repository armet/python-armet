

class TranscoderRegistry:
    """A registry used for registering and removing encoders and decoders.
    """
    def __init__(self):
        self.encoders = {}
        self.mime_types = {}

    def find(self, *, mime_type=None, name=None):
        # Attempt to find a compliant encoder given eitehr a mime_type or
        # encoder name.  Prioritize the mime-type.

        if mime_type is not None:
            return self.mime_types[mime_type]
        elif name is not None:
            return self.encoders[name]

        raise TypeError('Either mime_type or name is required.')

    def register(self, encoder, names, mime_types):
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
