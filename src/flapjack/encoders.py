""" ..
"""
import json
import datetime
import six
from .http import HttpResponse
from . import exceptions, transcoders, utils
from lxml.builder import E
from lxml import etree
from collections import Iterable

class Encoder(transcoders.Transcoder):

    @classmethod
    def encode(cls, obj=None):
        """
        Transforms objects into an acceptable format for tansmission.

        @returns
            An HttpResponse object containing all neccessary information
            that can be provided.
        """
        response = HttpResponse()
        if obj is not None:
            # We have an object; we need to encode it and set content
            # type, etc
            response.content = obj
            response['Content-Type'] = cls.mimetype

        # Pass on the constructed response
        return response


@Encoder.register()
class Json(transcoders.Json, Encoder):

    @staticmethod
    def default(obj):
        if isinstance(obj, datetime.datetime) \
                or isinstance(obj, datetime.date) \
                or isinstance(obj, datetime.time):
            return obj.isoformat()

        raise TypeError('{} is not JSON encodable.'.format(obj))

    @classmethod
    def encode(cls, obj=None):
        # Is this not a dictionary or an array?
        if not isinstance(obj, dict) and not isinstance(obj, list):
            # We need this to be at least a list for valid JSON
            obj = obj,

        # Encode nicely
        text = json.dumps(obj,
                ensure_ascii=True,
                separators=(',', ':'),
                default=cls.default
            )

        # Encode it normally; move along
        return super(Json, cls).encode(text)


@Encoder.register()
class Xml(transcoders.Xml, Encoder):

       #for each item in obj
           #if item is key-value pair
               #if value is iterable
                   #recursion!  See step 1.
               #else
                   #render key and value pair under root
           #else
               #if value is iterable
                   #recursion!  See step 1.
               #else
                   #insert the item into xml under root



    @classmethod
    def _encode_this_xml(cls,root,obj):
       #for each item in obj
       for key in obj:
           #if item is key-value pair
           try:
               #if value is iterable
               if isinstance(obj[key], Iterable) and not isinstance(obj[key],six.string_types):
                   #recursion!  See step 1.
                   sub = E.attribute( {'name':str(key)} )
                   cls._encode_this_xml(sub, obj[key])
                   root.append(sub)
               #else
               else:
#                   if isinstance(obj[key], datetime.date) \
#                    or isinstance(obj[key], datetime.time):
#                       obj[key] = obj[key].isoformat()
                   obj[key] = utils.fix_date(obj[key])
                   #insert key and value pair under root
                   root.append( E.attribute( str(obj[key]), {'name':str(key)}  ))
           #else
           except TypeError:
               #if value is iterable
               if isinstance(key, Iterable) and not isinstance(key,six.string_types):
                   #recursion!  See step 1.
                   sub = E.attribute( {'name':str(key)} )
                   cls._encode_this_xml(sub, key)
                   root.append(sub)
               #else
               else:
#                   if isinstance(key, datetime.date) \
#                    or isinstance(key, datetime.time):
#                       key = key.isoformat()
                   key = utils.fix_date(key)
               #render the item into xml under root
                   root.append( E.attribute( str(key) ))

    # Convert the obj param into an XML string
    @classmethod
    def encode(cls, obj=None):
        root = E.object()
        if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
           # We need this to be at least a list
           obj = obj,
        cls._encode_this_xml(root,obj)
        text = etree.tostring(root,pretty_print=True)
        return super(Xml, cls).encode(text)



@Encoder.register()
class Bin(transcoders.Bin, Encoder):

    @classmethod
    def encode(cls, obj=None):
        response = super(Bin, cls).encode(obj.read())
        response['Content-Disposition'] = \
            'attachment; filename="{}"'.format(obj.name.split('/')[-1])

        return response


@Encoder.register()
class Text(transcoders.Text, Encoder):


       #for each item in obj
           #if item is key-value pair

               #write out key after the corrent number of indents.
               #indent by length of key plus a few spaces
               
               #if item value is iterable
                   #recursion!  see step 1.
               #else
                   #output value.  Newline
                   
           #else
               #if value is iterable
                   #increment indent
                   #recursion!  See step 1.
               #else
                   #write out value after correct number of indents, then comma, then newline

    @classmethod
    def _encode_this_text(cls,obj,indent='',retval=''):
       #for each item in obj
       for key in obj:
           #if item is key-value pair
           try:
               obj[key]
               #write out key after the corrent number of indents
               retval += indent + str(key) + ':  ' 
               #if value is iterable
               if isinstance(obj[key], Iterable) and not isinstance(obj[key],six.string_types):
                   #recursion!  See step 1.
                   retval = cls._encode_this_text(obj[key],indent + (' ' * len(str(key)) ) + '   ',retval + '\n') + '\n'
               #else
               else:
                   #write out the value, then newline,
                   obj[key] = utils.fix_date(obj[key])
                   retval += str(obj[key]) + '\n'
           #else
           except TypeError:
               #if value is iterable
               if isinstance(key, Iterable) and not isinstance(key,six.string_types):
                   #recursion!  See step 1.
                   retval = cls._encode_this_text(key,indent + '   ',retval + '\n') + '\n'
               #else
               else:
                   key = utils.fix_date(key)
                   retval += indent + str(key) + '\n'
       return retval

    @classmethod
    def encode(cls, obj=None):
        if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
           # We need this to be at least a list
           obj = obj,
        textval = cls._encode_this_text(obj)
        #text = etree.tostring(root,pretty_print=True)
        return super(Text, cls).encode(textval)


#    @staticmethod
#    def _encode_value(value):
#        return str(value) if value is not None else ''

#    @staticmethod
#    def _encode_item(item):
#        try:
#            # Pretend we got a dictionary
#           return '\n'.join(
#                ' '.join((x, Text._encode_value(y))) for x, y in item.items())
#
#        except AttributeError:
            # We didn't; just return it
#            return str(item)

#    @classmethod
#    def encode(cls, obj=None):
#        if isinstance(obj, list):
            # Encode all the items
#            text = '\n\n'.join(Text._encode_item(x) for x in obj)

#        else:
            # Encode just the one item
#            text = Text._encode_item(obj)

#        return super(Text, cls).encode(text)


def find(request, format=None):
    """Determines the format to encode to and returns the encoder."""
    # Check locations where format may be defined in order of
    # precendence.
    if format is not None:
        # Format was provided through the URL via `.FORMAT`.
        format = format.lower()
        if format in Encoder.registry:
            return Encoder.registry[format]

        # Format was provided but unknown to us; we can do nothing in
        # this case

    elif request.META.get('HTTP_ACCEPT', None) is not None:
        # Use the encoding specified in the accept header
        encoder = Encoder.get(request.META['HTTP_ACCEPT'])
        if encoder is not None:
            return encoder

    # Failed to find an appropriate encoder
    # Get dictionary of available formats
    available = {k: v.mimetype for k, v in Encoder.registry.items()}

    # Encode the response using the appropriate exception
    raise exceptions.NotAcceptable(available)
