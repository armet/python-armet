# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into plain text.

@note
    This is close but not quite the `text/plain` mimetype defined in HTML5.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import datetime
import six
import os
import magic
import collections
from ..http import Response as HttpResponse
from urllib import quote_plus
from .. import transcoders
# from .. import exceptions, transcoders, utils
from . import Encoder, utils
from six.moves import cStringIO


class Encoder(transcoders.Text, Encoder):

    def _encode_mapping(self, stream, depth, obj):
        if depth:
            # We have some depth because we're inside a mapping;
            # get off the key line
            stream.write('\n')

        for key in obj:
            if depth:
                stream.write(' ' * depth * 2)
            stream.write('{}: '.format(key))
            self._encode_value(stream, depth + 1, obj[key])
            stream.write('\n')

    def _encode_sequence(self, stream, depth, obj):
        if depth:
            stream.write('\n')
        for value in obj:
            if depth:
                stream.write(' ' * depth * 2)
            self._encode_value(stream, depth, value)
            stream.write('\n')

    def _encode_value(self, stream, depth, obj):
        if obj is None:
            # We have nothing; and nothing in text is nothing.
            stream.write('')

        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            self._encode_value(stream, depth, obj.isoformat())

        elif isinstance(obj, six.string_types):
            # We have a string; simply return what we have.
            stream.write(obj.replace('\n', '\\n'))

        elif isinstance(obj, collections.Mapping):
            # Some kind of dictionary.
            self._encode_mapping(stream, depth, obj)

        elif isinstance(obj, collections.Sequence):
            # Some kind of sequence.
            self._encode_sequence(stream, depth, obj)

        elif isinstance(obj, six.integer_types):
            # Some kind of number.
            stream.write(str(obj))

        elif isinstance(obj, bool):
            # Boolean
            stream.write("true" if obj else "false")

        else:
            # We have no idea what we are..
            self._encode_value(stream, depth, utils.coerce_value(obj))

    def encode(self, obj=None):
        stream = cStringIO()
        self._encode_value(stream, 0, obj)
        result = stream.getvalue()
        stream.close()
        return result

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

    # @classmethod
    # def _encode_this_text(cls,obj,indent='',retval=''):
    #    #for each item in obj
    #    for key in obj:
    #        #if item is key-value pair
    #        try:
    #            obj[key]
    #            #write out key after the corrent number of indents
    #            retval += indent + str(key) + ':  '
    #            #if value is iterable
    #            if isinstance(obj[key], Iterable) and not isinstance(obj[key],six.string_types):
    #                #recursion!  See step 1.
    #                retval = cls._encode_this_text(obj[key],indent + (' ' * len(str(key)) ) + '   ',retval + '\n') + '\n'
    #            #else
    #            else:
    #                #write out the value, then newline,
    #                obj[key] = utils.fix_date(obj[key])
    #                retval += str(obj[key]) + '\n'
    #        #else
    #        except (TypeError, IndexError):
    #            #if value is iterable
    #            if isinstance(key, Iterable) and not isinstance(key,six.string_types):
    #                #recursion!  See step 1.
    #                retval = cls._encode_this_text(key,indent + '   ',retval + '\n') + '\n'
    #            #else
    #            else:
    #                key = utils.fix_date(key)
    #                retval += indent + str(key) + '\n'
    #    return retval

    # @classmethod
    # def encode(cls, obj=None):
    #     try:
    #         obj = base64.b64encode(obj.read())
    #         return super(Text,cls).encode(obj)
    #     except AttributeError:
    #         pass
    #     if not isinstance(obj, Iterable) or isinstance(obj,six.string_types):
    #        # We need this to be at least a list
    #        obj = obj,
    #     textval = cls._encode_this_text(obj)
    #     #text = etree.tostring(root,pretty_print=True)
    #     return super(Text, cls).encode(textval)
