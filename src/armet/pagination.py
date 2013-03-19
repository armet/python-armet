# -*- coding: utf-8 -*-
"""
Implementation of a pagination interface using a combination of the HTTP/1.1
range header and set specifiers.
"""

DEFAULT_RANGEWORD = 'items'
DEFAULT_PAGELENGTH = 20


def parse(specifiers):
    """
    Consumes set specifiers as text and forms a generator to retrieve
    the requested ranges.

    @param[in] specifiers
        Expected syntax is from the byte-range-specifier ABNF found in the
        [RFC 2616]; eg. 15-17,151,-16,26-278,15

    @returns
        Consecutive tuples that describe the requested range; eg. (1, 72) or
        (1, 1) [read as 1 to 72 or 1 to 1].
    """
    specifiers = "".join(specifiers.split())
    for specifier in specifiers.split(','):
        if len(specifier) == 0:
            raise ValueError("Range: Invalid syntax; missing specifier.")

        count = specifier.count('-')
        if (count and specifier[0] == '-') or not count:
            # Single specifier; return as a tuple to itself.
            yield int(specifier), int(specifier)
            continue

        specifier = map(int, specifier.split('-'))
        if len(specifier) == 2:
            # Range specifier; return as a tuple.
            if specifier[0] < 0 or specifier[1] < 0:
                # Negative indexing is not supported in range specifiers
                # as stated in the HTTP/1.1 Range header specification.
                raise ValueError(
                    "Range: Invalid syntax; negative indexing "
                    "not supported in a range specifier.")

            if specifier[1] < specifier[0]:
                # Range must be for at least one item.
                raise ValueError(
                    "Range: Invalid syntax; stop is less than start.")

            # Return them as a immutable tuple.
            yield tuple(specifier)
            continue

        # Something weird happened.
        raise ValueError("Range: Invalid syntax.")


def paginate(iterable, headers):
    """Paginate an iterable during a request.
    """
    # TODO: support dynamic rangewords and page lengths

    # Get the header
    header = headers.get('HTTP_RANGE')

    # do some validation
    prefix = DEFAULT_RANGEWORD + '='
    if not header or not header.find(prefix) == 0:
        # This is not using a range keyword that we understand
        ranges = ((0, DEFAULT_PAGELENGTH),)
    else:
        # Chop the prefix off the header and parse it
        ranges = parse(header[len(prefix):])

    # TODO: support multi-part range requests
    ranges = list(ranges)
    if len(ranges) > 1:
        raise NotImplementedError('multipart/byteranges')

    start, length = ranges[0]

    response_headers = {
        'Content-Range': '{}-{}/{}'.format(
            start,
            start + length,
            len(iterable)),
        'Accept-Ranges': DEFAULT_RANGEWORD
    }
    iterable = iterable[start:start + length + 1]
    return iterable, response_headers
