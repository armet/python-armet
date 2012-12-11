"""
Implements XML decoder.  Allows the server to consume XML into resources.
"""
import datetime
import six
#from ..http import Response
from .. import transcoders, utils
from dateutil.parser import parse
#from lxml.builder import E
from lxml import etree, objectify
from collections import Iterable, Mapping
from .. import transcoders
from . import Decoder


class Decoder(transcoders.Xml, Decoder):

    @classmethod
    def _insert_data(cls, retval, key, val):
        if key in retval:
            try:
                retval[key] = retval[key] + [ val ]
            except TypeError:
                retval[key] = [ retval[key] ]
                retval[key] = retval[key] + [ val ]
        else:
            retval[key] = val
        return retval

    @classmethod
    def _decode_xml(cls, obj):
       retval = {}

       if obj.getchildren() == []:
           return {obj.tag : obj.text}

       #for each item in obj
       for i in obj.iterchildren():
               #if value has children
               if i.countchildren() > 0:
                   #recursion! See step 1.
                   cls._insert_data(retval, i.tag, cls._decode_xml(i) )
#                   retval[i.tag] = cls._decode_xml(i)
               else:
                   #add a key-value pair to the retval
                   cls._insert_data(retval,i.tag,i.text)
       return retval

    @classmethod
    def decode(cls, request, attributes=None):
        nxml = objectify.fromstring(request.body)
        retval = cls._decode_xml(nxml)
        return retval
