# -*- coding: utf-8 -*-
"""
Implementation of a pagination interface using a combination of the HTTP/1.1
range header and set specifiers.
"""
from armet.http import exceptions, client

#! The range specifier to use.
RANGE_SPECIFIER = 'items'


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

        specifier = list(map(int, specifier.split('-')))
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


def paginate(request, response, items):
    """Paginate an iterable during a request.

    Magically splicling an iterable in our supported ORMs allows LIMIT and
    OFFSET queries. We should probably delegate this to the ORM or something
    in the future.
    """
    # TODO: support dynamic rangewords and page lengths
    # TODO: support multi-part range requests

    # Get the header
    header = request.headers.get('Range')
    if not header:
        # No range header; move along.
        return items

    # do some validation
    prefix = RANGE_SPECIFIER + '='
    if not header.find(prefix) == 0:
        # This is not using a range specifier that we understand
        raise exceptions.RequestedRangeNotSatisfiable()

    else:
        # Chop the prefix off the header and parse it
        ranges = parse(header[len(prefix):])

    ranges = list(ranges)
    if len(ranges) > 1:
        raise exceptions.RequestedRangeNotSatisfiable(
            'Multiple ranges in a single request is not yet supported.')

    start, end = ranges[0]

    # Make sure the length is not higher than the total number allowed.
    max_length = request.resource.count(items)
    end = min(end, max_length)

    response.status = client.PARTIAL_CONTENT
    response.headers['Content-Range'] = '%d-%d/%d' % (start, end, max_length)
    response.headers['Accept-Ranges'] = RANGE_SPECIFIER

    # Splice and return the items.
    items = items[start - 1:end]
    return items
