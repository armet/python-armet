import uuid
import collections
from io import BytesIO
from .general import register
from armet.codecs import FormDataCodec


def generate_boundary():
    """http://xkcd.com/221/"""
    return uuid.uuid4().hex


def generate_encoder(encoding):
    def retfn(string):
        return string.encode(encoding)
    return retfn


# Form data header sample:
# Content-Type: multipart/form-data; boundary=AaB03x

# The form data encoder should spit out something like this:
# --AaB03x
# Content-Disposition: form-data; name="submit-name"
#
# Larry
# --AaB03x
# Content-Disposition: form-data; name="files"; filename="file1.txt"
# Content-Type: text/plain
#
# ... contents of file1.txt ...
# --AaB03x--


def segment_stream(cache, buf, segment_size=16*1024):
    """Yields bytes in `segment_size` chunks from cache and then from buf.
    Operates by writing buf to cache and cleaning it every once in a while.
    Expects cache to be a BytesIO and buf to be a bytes.
    """
    while True:
        size = cache.tell()
        add = buf[:segment_size-size]
        buf = buf[segment_size-size:]
        cache.write(add)

        value = cache.getvalue()

        # Reset the cache.
        cache.truncate(0)
        cache.seek(0)

        if not len(value):
            break

        yield value


@register(
    names=FormDataCodec.names,
    mime_types=FormDataCodec.mime_types,
    preferred_mime_type=FormDataCodec.preferred_mime_type)
def form_encoder(data, encoding):
    """Expects to recieve a data structure of the following form:
    {name: value, name: [value1, value2]}
    """

    buf = BytesIO()
    encode = generate_encoder(encoding)
    boundary = encode(generate_boundary())

    # This function uses a lot of + to join strings,
    # this is because python3 does not allow for b'%s' % bytes()

    # Sanity check.
    if not isinstance(data, collections.Mapping):
        raise TypeError

    for name, values in data.items():
        # Normalize the values.
        if isinstance(values, str):
            values = (values,)
        elif not isinstance(values, collections.Sequence):
            # Sanity check.
            raise TypeError

        for entry in values:
            # Write the boundary for the next entry.
            buf.write(b'--' + boundary + b'\r\n')

            # Write the header for the next entry.
            # Note the extra new line afterwards.  This is because the next
            # entry is the value.
            bounds = (
                b'Content-Disposition: form-data; name=' +
                encode(name) +
                b'\r\n\r\n')

            buf.write(bounds)

            # Write the contents.
            # TODO: Make this stream the contents of entry
            yield from segment_stream(buf, encode(entry))

            # Write the trailing newline
            buf.write(b'\r\n')

    # All done.
    buf.write(b'--' + boundary + b'--')

    yield from segment_stream(buf, b'')
