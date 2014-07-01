
# Encoder registry
_ENCODERS = {}
_MIME_TYPE_ENCODERS = {}


def find(*, mime_type=None, name=None):
    # Attempt to find a compliant encoder given eitehr a mime_type or encoder
    # name.  Prioritize the mime-type.

    if mime_type is not None:
        return _MIME_TYPE_ENCODERS[mime_type]
    elif name is not None:
        return _ENCODERS[name]

    raise TypeError('Either mime_type or name is required.')


def register(encoder, names, mime_types):
    # Register the encoder provided in the global list of available encoders.
    _ENCODERS.update({x: encoder for x in names})
    _MIME_TYPE_ENCODERS.update({x: encoder for x in mime_types})


def purge(encoder):
    # Remove the encoder from the global list of available encoders.
    for registry in (_ENCODERS, _MIME_TYPE_ENCODERS):
        collection = set()
        for name, test in registry.items():
            if encoder is test:
                collection.add(name)

        # Need to apply the deletions after iterating over the registry
        # otherwise an exception is thrown because the dictionary changed
        # size during iteration.
        for key in collection:
            del registry[key]
