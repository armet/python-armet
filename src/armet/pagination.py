# -*- coding: utf-8 -*-
"""
Implementation of a pagination interface using a combination of the HTTP/1.1
range header and set specifiers.
"""
from armet import exceptions


def parse(specifiers):
    """
    Consumes set specifiers as text and forms a generator to retrieve
    the requested ranges.

    @param[in] specifiers
        Expected syntax is from the byte-range-specifier ABNF found in the
        [RFC 2616]; eg. 15-17,151,-16,26-278,15
    """
    specifiers = "".join(specifiers.split())
    for specifier in specifiers.split(','):
        if len(specifier) == 0:
            raise ValueError("Range: Invalid syntax; missing specifier.")

        count = specifier.count('-')
        if (count and specifier[0] == '-') or not count:
            # Single specifier; return as a tuple to itself.
            yield int(specifier), int(specifier); continue

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
            yield tuple(specifier); continue

        # Something weird happened.
        raise ValueError("Range: Invalid syntax.")

# DEFAULT_RANGEWORD = 'objects'
# DEFAULT_PAGELENGTH = 20

# class Paginator(object):
#     """Incredible Edible Paginator.  Interfaces with resources
#     """
#     def __init__(self, word=DEFAULT_RANGEWORD, length=DEFAULT_PAGELENGTH):
#         super(Paginator, self).__init__()
#         self.word = word
#         self.length = length

#         # Compile our regex after replacing the name
#         self.re = re.compile(RANGE_MATCH.format(name=word), re.X)

    # def paginate(self, iterable, headers):
    #     """Paginate an iterable during a request
    #     """
    #     # parse the pagination request header and get back the range requested
    #     if 'HTTP_RANGE' in headers:
    #         start, length = self.parse(headers['HTTP_RANGE'])
    #     else:
    #         # No range header, just set some defaults
    #         start = 0
    #         length = self.length
    #     response_headers = {
    #         'Content-Range': '{}-{}/{}'.format(
    #             start,
    #             start + length,
    #             len(iterable)),
    #         'Accept-Ranges': self.word
    #     }
    #     iterable = iterable[start:start + length + 1]
    #     return iterable, response_headers

    # def parse(self, header):
    #     """Parse the range header to figure out what page range the user
    #     requested
    #     """
    #     #! TODO:  The range header specification also allows multiple range
    #     #! sets.  See http://restpatterns.org/HTTP_Headers/Range
    #     #! In these situations, we're supposed to change the content-type to
    #     #! multipart/byteranges (or something similar).  Right now, we just
    #     #! throw if the user requested this.

    #     #! TODO: this regex sucks.  Build something that can deal with all the
    #     #! shennanigans that we can throw at it

    #     results = self.re.findall(header)

    #     try:
    #         # Verify that the matching word is the right one
    #         word = header.split('=')[0]
    #         if word != self.word:
    #             # Doesn't match
    #             raise exceptions.NotImplemented({
    #                 'Range':
    #                 'Paginating via {} is not implemented'.format(word)})

    #         # Verify that we only got one result
    #         if len(results) == 0:
    #             # Zero results?! they must have done it wrong
    #             # Possibly a 'objects=' sort of thing
    #             raise exceptions.BadRequest({
    #                 'Range':
    #                 'Invalid Syntax'
    #                 })
    #         if len(results) > 1:
    #             # More than one result is not yet implemented
    #             raise exceptions.NotImplemented({
    #                 'Range':
    #                 'multipart range requests are not implemented'
    #                 })

    #         # Just one result, lets check out what we got
    #         match = results[0]

    #         # Check for prefix and suffix stuff and populate start end attributes
    #         # None is special cased for end when we do not know how long it is
    #         if match[0] == '-':
    #             # Prefix match
    #             start = 0
    #             end = int(match[1:])
    #         elif match[-1] == '-':
    #             # Suffix match
    #             start = int(match[:-1])
    #             end = None
    #         elif match.find('-') != -1:
    #             # This is a range of objects, slice 'er up.
    #             start, end = match.split('-')

    #             # Cast to integers
    #             start = int(start)
    #             # End is inclusive, so add 1
    #             end = int(end)
    #         else:
    #             # Well this is just a number.  We only want to get 1 object
    #             start = int(match)
    #             end = start

    #     except ValueError:
    #         # word splitting went awry, we couldn't find an equals sign
    #         raise exceptions.BadRequest({
    #             'Range':
    #             'Invalid Syntax'
    #             })

    #     # return the start and the length of the pagination
    #     return start, end - start
