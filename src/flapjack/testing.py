from django.utils import unittest
from django.test.client import Client
from lxml import etree
import json

#commonly-used functions for testes
@staticmethod
def ensureValidXMLResponse(responsebody):
    try:
        etree.fromstring(responsebody)
    except etree.XMLSyntaxError:
        assertEqual(False, "problem! this is not really XML!")
        print responsebody

@staticmethod
def ensureValidJSONResponse(responsebody):
    try:
        json.loads(responsebody)
    except ValueError:
        assertEqual(False, "problem! this is not really JSON!")
        print responsebody
        
@staticmethod
def ensureOKResponse(response_code):
    assertEqual(response_code, 200) #Magic number used here; fix later

@staticmethod
def ensureOKValidXML(response):
    ensureValidXMLResponse(response.content)
    ensureOKResponse(response.status_code)
    
@staticmethod
def ensureOKValidJSON(response):
    ensureValidJSONResponse(response.content)
    ensureOKResponse(response.status_code)
    
class FlapjackUnitTest(unittest.TestCase):
    """Unit Tests base class"""
    
    #I want to create a new client that extends the built-in django client.
    #I want it to automatically test for 500 errors.
    #It can handle the 500 error however we want it to; by logging to a log file, raising an exception,
    #or whatever.
    class FlapjackRESTClient(Client):
        def get(cls, path, data={}, follow=False, **extra):
            response = super(FlapjackUnitTest.FlapjackRESTClient, cls).get(path=path,data=data,follow=follow,**extra)
            if response.status_code >= 500:
                raise Exception("500 error! Not acceptable.")
            return response
            
        def post(cls, path, data={}, follow=False, **extra):
            response = super(FlapjackRESTClient, cls).post(path=path,data=data,follow=follow,**extra)
            if response.status_code >= 500:
                raise Exception("500 error! Not acceptable.")
            return response
            
        def put(cls, path, data={}, content_type='application/octet-stream', follow=False, **extra):
            response = super(FlapjackRESTClient, cls).put(path=path,data=data,content_type=content_type,follow=follow,**extra)
            if response.status_code >= 500:
                raise Exception("500 error! Not acceptable.")
            return response
            
        def delete(cls, path, data={}, content_type='application/octet-stream', follow=False, **extra):
            response = super(FlapjackRESTClient, cls).delete(path=path,data=data,content_type=content_type,follow=follow,**extra)
            if response.status_code >= 500:
                raise Exception("500 error! Not acceptable.")
            return response
    
    def setUp(self):
         self.c = self.FlapjackRESTClient()

