""" ..
"""
import datetime
import six
from ..http import Response
from .. import transcoders, utils
from lxml.builder import E
from lxml import etree
from collections import Iterable, Mapping
from .. import transcoders
from . import Encoder


def _encode_file_into_xml(e,obj):
        data = obj.read()
        base64_string = base64.b64encode(data)
        e.text = base64_string

class Encoder(transcoders.Xml, Encoder):

    @classmethod
    def _iterate_thru_object(cls,root,obj):
       for key in obj:
           try:
               if isinstance(obj[key], Iterable) and not isinstance(obj[key],six.string_types):
                   #recursion! See step 1.

                   sub = E.attribute( {'name':str(key)} )

                   cls._iterate_thru_object(sub, obj[key])

                   root.append(sub)
               else:
                   # item is NOT iterable; no recursion needed
                   if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
                       obj = obj.isoformat() # fix date

                   #insert key and value pair under root
                   root.append( E.attribute( str(obj[key]), {'name':str(key)} ))

           #obj is NOT a dictionary
           except (TypeError, IndexError):
               if isinstance(key, Iterable) and not isinstance(key,six.string_types):
                   #recursion! See step 1.

                   # if the key is a dictionary, it means it is an object, not attribute
                   if type(key) == type({}):
                       sub = E.object()

                   else:
                       sub = E.attribute( {'name':str(key)} )

                   cls._iterate_thru_object(sub, key)
                   root.append(sub)
               else:
                   if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
                       obj = obj.isoformat() # fix date

                   # insert value, not attribute
                   root.append( E.value( str(key) ))
                   
    @classmethod
    def _encode_object_into_xml(cls,obj):
    
    
        e = E.object()
        if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
           obj = obj,
        
        elif not isinstance(obj, Mapping):
           e = E.objects()

        cls._iterate_thru_object(e,obj)
            
        return e

    @classmethod
    def encode(cls, obj=None):
        try:
            e = E.data()
            _encode_file_into_xml(e,obj)
            text = etree.tostring(e,pretty_print=False)
            return text
        except:
            root = cls._encode_object_into_xml(obj)
            return etree.tostring(root,pretty_print=True)
