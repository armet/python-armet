""" ..
"""
import datetime
import six
#from ..http import HttpResponse
from ..http import Response
from .. import transcoders, utils
from lxml.builder import E
from lxml import etree
from collections import Iterable, Mapping
from .. import transcoders
from . import Encoder


#This is simply a procedural call. Not a member function
def _encode_file_into_xml(e,obj):
        data = obj.read()
        base64_string = base64.b64encode(data)
        e.text = base64_string

#class Xml(transcoders.Xml):
class Encoder(transcoders.Xml, Encoder):

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
    def _iterate_thru_object(cls,root,obj):
       #for each item in obj
       for key in obj:
           
           #if item is key-value pair
           try:
               #if value is iterable
               if isinstance(obj[key], Iterable) and not isinstance(obj[key],six.string_types):
                   #recursion!  See step 1.

                   sub = E.attribute( {'name':str(key)} )

                   cls._iterate_thru_object(sub, obj[key])

                   root.append(sub)
               #else
               else:
                   obj[key] = utils.fix_date(obj[key])
                   #insert key and value pair under root
                   root.append( E.attribute( str(obj[key]), {'name':str(key)}  ))
           #else
           except (TypeError, IndexError):
               #if value is iterable
               if isinstance(key, Iterable) and not isinstance(key,six.string_types):
                   #recursion!  See step 1.

                   # if the key is a dictionary, it means it is an object, not attribute
                   if type(key) == type({}):
                       sub = E.object()
                   # if the item is a list, just recur through the list
                   else:
                       sub = E.attribute( {'name':str(key)} )

#                   sub = E.attribute( {'name':str(key)} )

                   cls._iterate_thru_object(sub, key)
                   root.append(sub)
               #else
               else:
                   key = utils.fix_date(key)
               #render the item into xml under root
                   root.append( E.value( str(key) ))
                   
    @classmethod
    def _encode_object_into_xml(cls,obj):
    
    
        e = E.object()
        if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
           # We need this to be at least a list
           obj = obj,
        
        elif not isinstance(obj, Mapping):
           e = E.objects()

        cls._iterate_thru_object(e,obj)
            
        return e

    # Convert the obj param into an XML string
    @classmethod
    def encode(cls, obj=None):
        #is there a better way to test for file?
        try:
            e = E.data()
            _encode_file_into_xml(e,obj)
            text = etree.tostring(e,pretty_print=False)
            return text
        except:
            root = cls._encode_object_into_xml(obj)
            return etree.tostring(root,pretty_print=True)

#TODO: fix these hacks
