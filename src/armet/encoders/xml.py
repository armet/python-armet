""" 
Implements XML encoder.  Allows the server to send any resource in XML format.
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
    def _process_xml_info(cls,root,info,name=None):
        # call function if needed
        try:
            info = info()
        except TypeError:
            pass

        if isinstance(info, Iterable) and not isinstance(info,six.string_types):
            #recursion! See step 1.
            if isinstance(info, dict):
                sub = E.object()
            else:
                sub = E.attribute( {'name': name } )
            for key in info:
                cls._insert_data_into_tree(sub,key,info)
            root.append(sub)

        else:
            try:
                info = info.isoformat()
            except AttributeError:
                pass
            if name is None:
                root.append( E.value( str(info) ) )
            else:
                root.append(E.attribute( str(info), {'name': name} ) )

    @classmethod
    def _insert_data_into_tree(cls,root,key,obj=None):
           try:
               cls._process_xml_info(root, obj[key], str(key) )
           except (TypeError, IndexError):
               cls._process_xml_info(root, key)

    @classmethod
    def _iterate_thru_object(cls,root,obj):
       for key in obj:
           cls._insert_data_into_tree(root,key,obj)
                   
    @classmethod
    def _encode_object_into_xml(cls,obj):
    
        e = E.object()
        primitive = (int, six.string_types, datetime.time, datetime.date)

        if isinstance(obj,primitive):
            cls._insert_data_into_tree(e,obj)
            return e
        
        if not isinstance(obj, Iterable):

            result = utils.coerce_dict(obj)

            cls._iterate_thru_object(e,result)
            return e
        
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
