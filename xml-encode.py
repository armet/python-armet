# from lxml import etree
# from lxml.builder import ElementMaker
# import six
# from lxml import objectify
import xml.etree.ElementTree as ElementTree


class XmlDictConfig(dict):
    def __init__(self, aDict):
        bDict = {}
        for element in aDict:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    bDict = {element.tag: XmlDictConfig(element)}
                else:
                    bDict = {element[0].tag: XmlDictConfig(element)}
                if element.items():
                    bDict.update(dict(element.items()))
            elif element.items():
                bDict.update({element.tag: dict(element.items())})
            else:
                bDict.update({element.tag: element.text})
        self.update(bDict)


class XmlParser():
    def xmlToDict(self, parent_element):
        aDict = {}
        if parent_element.items():
            aDict.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    bDict = XmlDictConfig(element)
                else:
                    bDict = {element[0].tag: XmlDictConfig(element)}
                if element.items():
                    bDict.update(dict(element.items()))
                aDict.update({element.tag: bDict})
            elif element.items():
                aDict.update({element.tag: dict(element.items())})
            else:
                aDict.update({element.tag: element.text})
        return aDict

    def dictToXml(self, aDict):
        elem = ElementTree.Element("xml")
        # print "Element object:", elem
        for key, value in aDict.items():
            if isinstance(value, type(0)):
                ElementTree.SubElement(elem, key, type="int").text = str(value)
            elif isinstance(value, dict):
                test = self.dictToString(ElementTree.Element(key), value)
                ElementTree.SubElement(elem, key).text = test
            else:
                ElementTree.SubElement(elem, key).text = value
        dictAsXML = ElementTree.tostring(elem)
        dictAsXML = dictAsXML.replace("&lt;", "<")
        dictAsXML = dictAsXML.replace("&gt;", ">")
        return dictAsXML

    def encode(self, obj):
        root = ElementTree.Element('xml')
        for key, value in obj.items():
            if isinstance(value, int):
                ElementTree.SubElement(root, key, type='integer').text = str(value)
            elif isinstance(value, dict):
                text = self.tostring(ElementTree.Element(key), value)
                ElementTree.SubElement(root, key).text = 
            else:
                ElementTree.SubElement(root, key)
        xml = ElementTree.tostring(root)
        xml = xml.replace('&lt;', '<')
        xml = xml.replace('&gt;', '>')
        return xml

    def tostring(self, element, obj):
        container = []
        for key, value in obj.items():
            if isinstance(value, int):
                ElementTree.SubElement(element, key, type='integer').text = str(value)
            elif isinstance(value, dict):
                ElementTree.SubElement(element, key).text = self.tostring(key, value)
            else:
                ElementTree.SubElement(element, key).text = value
                container.append('<{0}>{1}</{0}>'.format(key, value))
        return ''.join(container)

    def dictToString(self, elem, aDict):
        aList = []
        for key, value in aDict.items():
            if isinstance(value, type(0)):
                ElementTree.SubElement(elem, key, type="int").text = str(value)
            elif isinstance(value, dict):
                print "Element is a dict"
                ElementTree.SubElement(elem, key).text = self.dictToString(
                    key, value)
            else:
                ElementTree.SubElement(elem, key).text = value
                aList.append("<" + key + ">" + value + "</" + key + ">")
        return ''.join(aList)

root = ElementTree.XML('<?xml version="1.0" encoding="ISO-8859-1"?><context><namespace><prefix>org.instantknowledge.com.</prefix><context>battery</context></namespace><data><state>86%</state><charging>false</charging></data></context>')

xmldict = XmlParser().xmlToDict(root)

print xmldict

print XmlParser().dictToXml(xmldict)
