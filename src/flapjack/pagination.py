"""PAGINATION!
We're not using the django paginator class here because its focused on
page number based pagination rather than start/offset pagination that the
http range header uses
"""

import re
from . import exceptions

DEFAULT_RANGEWORD = 'objects'
DEFAULT_PAGELENGTH = 20
RANGE_MATCH = r"""
    # This regex is intending to match one of these:
    # bytes=222,3,bytes=55-2123,-134,51354-12321

    # The rangeword that we need to match against (no capture) trailing
    # question mark because this will modify the next regex string (each number
    # may or may not be prefixed with a name= block)
    (?:^{name}=)?

    # just match digit hyphen stuff
    ((?:-)?\d+(?:-\d+)?)+
"""


class Paginator(object):
    """Incredible Edible Paginator.  Interfaces with resources
    """
    def __init__(self, word=DEFAULT_RANGEWORD, length=DEFAULT_PAGELENGTH):
        super(Paginator, self).__init__()
        self.word = word
        self.length = length

        # Compile our regex after replacing the name
        self.re = re.compile(RANGE_MATCH.format(name=word), re.X)

    def paginate(self, iterable, headers):
        """Paginate an iterable during a request
        """
        # parse the pagination request header and get back the range requested
        if 'HTTP_RANGE' in headers:
            start, length = self.parse(headers['HTTP_RANGE'])
        else:
            # No range header, just set some defaults
            start = 0
            length = self.length
        response_headers = {
            'Content-Range': '{}-{}/{}'.format(
                start,
                start + length,
                len(iterable)),
            'Accept-Ranges': self.word
        }
        iterable = iterable[start:start + length + 1]
        return iterable, response_headers

    def parse(self, header):
        """Parse the range header to figure out what page range the user
        requested
        """
        #! TODO:  The range header specification also allows multiple range
        #! sets.  See http://restpatterns.org/HTTP_Headers/Range
        #! In these situations, we're supposed to change the content-type to
        #! multipart/byteranges (or something similar).  Right now, we just
        #! throw if the user requested this.

        #! TODO: this regex sucks.  Build something that can deal with all the
        #! shennanigans that we can throw at it

        results = self.re.findall(header)

        try:
            # Verify that the matching word is the right one
            word = header.split('=')[0]
            if word != self.word:
                # Doesn't match
                raise exceptions.NotImplemented({
                    'Range':
                    'Paginating via {} is not implemented'.format(word)})

            # Verify that we only got one result
            if len(results) == 0:
                # Zero results?! they must have done it wrong
                # Possibly a 'objects=' sort of thing
                raise exceptions.BadRequest({
                    'Range':
                    'Invalid Syntax'
                    })
            if len(results) > 1:
                # More than one result is not yet implemented
                raise exceptions.NotImplemented({
                    'Range':
                    'multipart range requests are not implemented'
                    })

            # Just one result, lets check out what we got
            match = results[0]

            # Check for prefix and suffix stuff and populate start end fields
            # None is special cased for end when we do not know how long it is
            if match[0] == '-':
                # Prefix match
                start = 0
                end = int(match[1:])
            elif match[-1] == '-':
                # Suffix match
                start = int(match[:-1])
                end = None
            elif match.find('-') != -1:
                # This is a range of objects, slice 'er up.
                start, end = match.split('-')

                # Cast to integers
                start = int(start)
                # End is inclusive, so add 1
                end = int(end)
            else:
                # Well this is just a number.  We only want to get 1 object
                start = int(match)
                end = start

        except ValueError:
            # word splitting went awry, we couldn't find an equals sign
            raise exceptions.BadRequest({
                'Range':
                'Invalid Syntax'
                })

        # return the start and the length of the pagination
        return start, end - start
