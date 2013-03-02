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

    def test(self, obj):
        xml = None
        root = ElementTree.Element('xml')
        if not isinstance(obj, str):
            for key, value in obj.items():
                if isinstance(value, int):
                    ElementTree.SubElement(root, key,
                        type='integer').text = bytes(str(value))
                elif isinstance(value, dict):
                    text = self.dict_to_string(ElementTree.Element(key), value)
                    ElementTree.SubElement(root, key).text = text
                elif isinstance(value, datetime.time) or isinstance(value, datetime.date):
                    ElementTree.SubElement(root, key).text = value.isoformat()
                elif isinstance(value, list):
                    node = ElementTree.SubElement(root, key)
                    print(node)
                    for item in value:
                        ElementTree.SubElement(node, key).text = item
                else:
                    ElementTree.SubElement(root, key).text = bytes(str(value))

            xml = ElementTree.tostring(root)
        # else:
        #     xml = ElementTree.
            
        xml = xml.replace('&lt;', '<')
        xml = xml.replace('&gt;', '>')
        return xml

    def encode(self, obj=None):
        xml_dict = self._encode_value(obj)
        val = ''  # ...
        if isinstance(xml_dict, list):
            for item in xml_dict:
                val += self.test(item)
        elif isinstance(xml_dict, str):
            val = xml_dict
        else:
            print(type(xml_dict))
            val = self.test(xml_dict)
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
        print('LOLOLOL')
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
