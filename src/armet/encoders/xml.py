from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import xml.etree.ElementTree as ElementTree
from .. import transcoders
from . import Encoder


class Encoder(transcoders.Xml, Encoder):

    def encode(self, obj):
        print(type(obj))
        root = ElementTree.Element('xml')
        for key, value in obj.items():
            if isinstance(value, int):
                ElementTree.SubElement(root, key,
                    type='integer').text = str(value)
            elif isinstance(value, dict):
                text = self.tostring(ElementTree.Element(key), value)
                ElementTree.SubElement(root, key).text = text
            else:
                ElementTree.SubElement(root, key).text = str(value)
        xml = ElementTree.tostring(root)
        xml = xml.replace('&lt;', '<')
        xml = xml.replace('&gt;', '>')
        return xml

    def tostring(self, element, obj):
        container = []
        for key, value in obj.items():
            if isinstance(value, int):
                ElementTree.SubElement(element, key,
                    type='integer').text = str(value)
            elif isinstance(value, dict):
                ElementTree.SubElement(element,
                    key).text = self.tostring(key, value)
            else:
                ElementTree.SubElement(element, key).text = value
                container.append('<{0}>{1}</{0}>'.format(key, value))
        return ''.join(container)
