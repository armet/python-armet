""" ..
"""
import abc
import json
import datetime
from dateutil.parser import parse
from . import exceptions, transcoders
from lxml import etree
from lxml import objectify

class Decoder(transcoders.Transcoder):

    @classmethod
    @abc.abstractmethod
    def decode(cls, request, fields):
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


@Decoder.register()
class Form(transcoders.Form, Decoder):

    @classmethod
    def decode(cls, request, fields):
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
            try:
                if len(item) == 1 and not fields[name].collection:
                    obj[name] = item[0]

            except KeyError:
                # Weird..
                pass

        # Return the final object dictionary
        return obj


@Decoder.register()
class Url(transcoders.Url, Decoder):
    decode = Form.decode


@Decoder.register()
class Json(transcoders.Json, Decoder):

    @staticmethod
    def object_hook(obj):
        # Iterate and attempt to parse any date/time like values
        for name, value in obj.iteritems():
            if not isinstance(value, basestring):
                # Not a string; move along.
                continue

            if not value:
                # Empty string move along
                continue

            try:
                obj[name] = parse(value)

            except ValueError:
                # Guess it wasn't a date
                pass

        return obj

    @classmethod
    def decode(cls, request, fields):
        cls.fields = fields  # HACK: Get rid of this hack
        retval = json.loads(request.body, object_hook=cls.object_hook)
        #print retval
        return retval

@Decoder.register()
class Xml(transcoders.Xml, Decoder):

    @classmethod
    def _iter_stuff(cls, fields, stuff):
    #I know I wrote this code, but I see it has a problem.
    #It only works when the root node has sub nodes.  Must fix.

    #The only reason I haven't fixed it yet is that the PUT
    #method for resource fields isn't working.  So it would
    #impossible to test that the XML decoder is working
    #correctly.

       retval = {}
       #for each item in obj
       for i in stuff.iterchildren():
               #if value is has children
               if i.countchildren() > 0:
                   #recursion!  See step 1.
                   cls.iter_stuff(fields, stuff)
               else:
                   #add a key-value pair to the retval
                   try:
                       #time manipulation
                       try:
                        int(i.text)
                        retval[i.attrib['name']] = i.text
                       except ValueError:
                        retval[i.attrib['name']] = parse(i.text)
                   except ValueError:
                       retval[i.attrib['name']] = i.text
       return retval

    @classmethod
    def decode(cls, request, fields):
        nxml = objectify.fromstring(request.body)
        retval = cls._iter_stuff(fields, nxml)
        return retval


def find(request):
    """Determines the format to decode to and returns the decoder."""
    # Grab the content type header to get the mimetypes requested; defaults
    # to `application/octet-stream` as defined by HTTP/1.1 -- wonder how
    # we'll support that
    mimetype = request.META.get('CONTENT_TYPE', 'application/octet-stream')

    # Attempt to find a decoder and on failure, die.
    decoder = Decoder.get(mimetype)
    if decoder is None:
        # Failed to find an appropriate decoder; we have no idea how to
        # handle the data.
        raise exceptions.UnsupportedMediaType()

    return decoder
