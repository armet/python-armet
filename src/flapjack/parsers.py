""" ..
"""
import abc
import mimeparse


class Parser(object):
    #! Applicable mimetypes for this parser
    mimetypes = []

    @classmethod
    def can_parse(cls, content_type_header):
        """
        Determine if this parser can deserialize an appropriate message
        specified by the CONTENT-TYPE header.
        """
        return mimeparse.best_match(cls.mimetypes, content_type_header) != ''

    @abc.abstractmethod
    def parse(cls, request):
        """
        Constructs an object dictionary from the request body according to the
        media-type specified in the `Content-Type` header.

        @param[in] request
            Django request object containing the request body (at a minimum:
            body, POST, and FILES).

        @returns
            A dictionary containing the parameters of the request.
        """
        pass


class FormData(Parser):
    #! Applicable mimetypes for this parser
    mimetypes = [
        'multipart/form-data'
    ]

    @classmethod
    def parse(cls, request):
        # Build the initial object as a copy of the POST data
        obj = dict(request.POST)

        # Iterate through this absurd multi-value-dict and multiplex the
        # values into obj
        for name in request.FILES:
            if name not in obj:
                obj[name] = []

            obj[name].extend(request.FILES.getlist(name))

        # Now flatten those in that can be flattened
        for name, item in obj.items():
            if len(item) == 1:
                obj[name] = item[0]

        # Return the final object dictionary
        return obj


# TODO: Find a more fun way to keep track of parsers
parsers = [
    FormData
]


def get(request):
    if 'CONTENT_TYPE' not in request.META:
        # No accept header provided; we can do nothing as the default
        # is application/octet-stream.
        # TODO: Perhaps devise a way to accept this ?
        return None

    content_type = request.META['CONTENT_TYPE']
    for parser in parsers:
        if parser.can_parse(content_type):
            # Parser matched against the type header; return it
            return parser

    # Nothing can be matched; return nothing
