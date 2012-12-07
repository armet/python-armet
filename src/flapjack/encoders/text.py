""" ..
"""
import datetime
import six
import magic
from ..http import Response as HttpResponse
from .. import exceptions, transcoders, utils

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
           except (TypeError, IndexError):
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
        try:
            obj = base64.b64encode(obj.read())
            return super(Text,cls).encode(obj)
        except AttributeError:
            pass
        if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
           # We need this to be at least a list
           obj = obj,
        textval = cls._encode_this_text(obj)
        #text = etree.tostring(root,pretty_print=True)
        return super(Text, cls).encode(textval)
