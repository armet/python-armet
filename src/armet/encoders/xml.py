from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections import Iterable, Mapping
from types import GeneratorType
import collections
import xml.etree.ElementTree as ElementTree
import datetime
import six
import decimal
import fractions
from .. import transcoders
from . import Encoder, utils


class Encoder(transcoders.Xml, Encoder):

    def dict_to_xml(self, obj):
        xml = None
        # the root element. I guess xml will be fine.
        root = ElementTree.Element('xml')

        # this will need to be redone still .... for now it works
        # if it's not a dict it's a string and just returned 
        # to the api as a plain string
        if isinstance(obj, dict):
            for key, value in obj.items():

                # if integer
                if isinstance(value, int):
                    ElementTree.SubElement(root, key,
                        type='integer').text = bytes(str(value))

                # if a list, loop through grab each item
                elif isinstance(value, list):
                    node = ElementTree.SubElement(root, key)
                    for item in value:
                        ElementTree.SubElement(node, key).text = item

                # if a dict, convert to string
                elif isinstance(value, dict):
                    text = self.dict_to_string(ElementTree.Element(key), value)
                    ElementTree.SubElement(root, key).text = text

                # date format
                elif isinstance(value, datetime.time) or isinstance(value, datetime.date):
                    ElementTree.SubElement(root, key).text = value.isoformat()

                # ...
                else:
                    ElementTree.SubElement(root, key).text = bytes(str(value))

            xml = ElementTree.tostring(root)

        # remote html crap
        xml = xml.replace('&lt;', '<')
        xml = xml.replace('&gt;', '>')
        return xml

    def encode(self, obj=None):
        xml_dict = self._encode_value(obj)
        val = ''  # ...
        # this covers the list view (e.g. /api/polls.xml)
        if isinstance(xml_dict, list):
            for item in xml_dict:
                val += self.dict_to_xml(item)

        # if dict, convert to xml
        elif isinstance(xml_dict, dict):
            val = self.dict_to_xml(xml_dict)

        # just send back the damn object...
        else:
            val = obj

        return val

    def _encode_value(self, obj):
        if obj is None:
            # We have nothing; and nothing in text is nothing.
            return None

        if isinstance(obj, datetime.time) or isinstance(obj, datetime.date):
            # This is some kind of date/time -- encode using ISO format.
            return self._encode_value(obj.isoformat())

        if isinstance(obj, six.string_types):
            # We have a string; simply return what we have.
            return bytes(obj)

        if isinstance(obj, collections.Mapping):
            # Some kind of dictionary.
            return {bytes(key): self._encode_value(obj[key]) for key in obj}

        if isinstance(obj, collections.Sequence):
            # Some kind of sequence.
            return [self._encode_value(item) for item in obj]

        if isinstance(obj, six.integer_types):
            # Some kind of number.
            return bytes(obj)

        if isinstance(obj, (float, fractions.Fraction, decimal.Decimal)):
            # Some kind of something.
            return bytes(obj)

        if isinstance(obj, bool):
            # Boolean.
            return b"true" if obj else b"false"

        # We have no idea what we are..
        return self._encode_value(utils.coerce_value(obj))

    def dict_to_string(self, element, obj):
        container = []
        for key, value in obj.items():
            if isinstance(value, int):
                ElementTree.SubElement(element, key,
                    type='integer').text = str(value)
            elif isinstance(value, dict):
                ElementTree.SubElement(element,
                    key).text = self.dict_to_string(key, value)
            else:
                ElementTree.SubElement(element, key).text = value
                container.append('<{0}>{1}</{0}>'.format(key, value))
        return ''.join(container)
