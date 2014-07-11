import cgi
import operator
import io

from ..codecs import FormCodec
from . import register


# FIXME: This expects a "boundary" property that it won't get, ever.
# FIXME: This is quite slow (guess is that is because of "cgi")
@register(name="form", mime_type=FormCodec.mime_types)
def decode(text, boundary):
    fp = io.BytesIO(text)
    result = cgi.parse_multipart(fp, {'boundary': boundary.encode('utf8')})

    # We need to operate on the values to decode them and to unpack shallow
    # ones.
    keys, values = zip(*result.items())

    # Decode the values
    decode = operator.methodcaller('decode', 'utf8')
    values = (list(map(decode, entry)) for entry in values)

    # Unpack shallow values (where there's only one)
    values = (x if len(x) > 1 else x[0] for x in values)

    # Return the dictionary!
    return dict(zip(keys, values))
