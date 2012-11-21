from django.utils import unittest
from django.test.client import Client
from lxml import etree
import json

#I want to create a new client that extends the built-in django client.
#I want it to automatically test for 500 errors.
#It can handle the 500 error however we want it to; by logging to a log file, raising an exception,
#or whatever.
class FlapjackRESTClient(Client):
    def get(cls, path, data={}, follow=False, **extra):
        response = super(FlapjackRESTClient, cls).get(path=path,data=data,follow=follow,**extra)
#            if response.status_code >= 500:
#                raise Exception("500 error! Not acceptable.")
        return response
        
    def post(cls, path, data={}, follow=False, **extra):
        response = super(FlapjackRESTClient, cls).post(path=path,data=data,follow=follow,**extra)
#            if response.status_code >= 500:
#                raise Exception("500 error! Not acceptable.")
        return response
        
    def put(cls, path, data={}, content_type='application/octet-stream', follow=False, **extra):
        response = super(FlapjackRESTClient, cls).put(path=path,data=data,content_type=content_type,follow=follow,**extra)
#            if response.status_code >= 500:
#                raise Exception("500 error! Not acceptable.")
        return response
        
    def delete(cls, path, data={}, content_type='application/octet-stream', follow=False, **extra):
        response = super(FlapjackRESTClient, cls).delete(path=path,data=data,content_type=content_type,follow=follow,**extra)
#            if response.status_code >= 500:
#                raise Exception("500 error! Not acceptable.")
        return response

class FlapjackUnitTest(unittest.TestCase):
    """Unit Tests base class"""
    
    def setUp(self):
         self.c = FlapjackRESTClient()

    #commonly-used functions for tests
    def assertValidXMLResponse(self, response, content-type='application/xml'):
        failtext = ""
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            failtext = "Invalid XML in response \n"
        if response['Content-Type'] != content-type:
            failtext += "Content-Type header not " + content-type " as expected; is " + response['Content-Type']
        if failtext != "":
            self.fail(failtext)
    
    def assertValidJSONResponse(self, response, content-type='application/json'):
        failtext = ""
        try:
            json.loads(response.content)
        except ValueError:
            failtext = "Invalid JSON in response \n"
        if response['Content-Type'] != 'application/json':
            failtext += "Content-Type header not " + content-type " as expected; is " + response['Content-Type']
        if failtext != "":
            self.fail(failtext)
            
    def assertOKValidXML(self, response):
        self.assertValidXMLResponse(response)
        self.assertOKResponse(response)
        
    def assertOKValidJSON(self, response):
        self.assertValidJSONResponse(response)
        self.assertOKResponse(response)
        
    def assertOKResponse(self, response):
        self.assertEqual(response.status_code, 200) #Magic number used here; fix later
    
