# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import itertools
from django.utils import unittest
from armet import encoders


class XmlTestCase(unittest.TestCase):

    def setUp(self):
        self.xml = encoders.Xml()
        self.message = {
            'this': 'that',
            'answer': 42,
            'bool': True,
            'list': [
                {'foo': 'bar', 'foo2': 'bar2'},
                {'tag': 'text', 'tag2': 'text2'},
                {'item': 'something', 'value': 'else'},
            ]
        }

    def test_xml_none(self):
        rendered = self.xml.encode(None)
        self.assertEqual(rendered, '<object/>')

    def test_xml_bool(self):
        rendered = self.xml.encode(True)
        self.assertEqual(rendered, '<object><value>True</value></object>')

    def test_xml_dict(self):
        rendered = self.xml.encode(self.message)
        self.assertEqual(rendered, '<object><this>that</this><answer>42</answer><list><object><foo>bar</foo><foo2>bar2</foo2></object><object><tag>text</tag><tag2>text2</tag2></object><object><item>something</item><value>else</value></object></list><bool>True</bool></object>')

    def test_xml_list(self):
        message = [self.message for x in range(4)]
        rendered = self.xml.encode(message)


        self.assertEqual(rendered, '<objects><object><this>that</this><answer>42</answer><list><object><foo>bar</foo><foo2>bar2</foo2></object><object><tag>text</tag><tag2>text2</tag2></object><object><item>something</item><value>else</value></object></list><bool>True</bool></object><object><this>that</this><answer>42</answer><list><object><foo>bar</foo><foo2>bar2</foo2></object><object><tag>text</tag><tag2>text2</tag2></object><object><item>something</item><value>else</value></object></list><bool>True</bool></object><object><this>that</this><answer>42</answer><list><object><foo>bar</foo><foo2>bar2</foo2></object><object><tag>text</tag><tag2>text2</tag2></object><object><item>something</item><value>else</value></object></list><bool>True</bool></object><object><this>that</this><answer>42</answer><list><object><foo>bar</foo><foo2>bar2</foo2></object><object><tag>text</tag><tag2>text2</tag2></object><object><item>something</item><value>else</value></object></list><bool>True</bool></object></objects>')

#TODO
"""    def test_xml_generator(self):
        message, save = itertools.tee((self.message for x in range(3)))
        rendered = self.xml.encode(message)


        self.assertEqual(rendered, list(save))

    def test_xml_object(self):
        rendered = self.xml.encode(type(b'message', (), self.message))


        self.assertEqual(rendered, self.message) """
