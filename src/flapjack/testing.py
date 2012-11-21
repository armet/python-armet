from django.utils import unittest
from django.test.client import Client
from http import status
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
    def assertValidXMLResponse(self, response, contenttype='application/xml'):
        failtext = ""
        try:
            etree.fromstring(response.content)
        except etree.XMLSyntaxError:
            failtext = "Invalid XML in response \n"
        if response['Content-Type'] != contenttype:
            failtext += "Content-Type header not " + contenttype + " as expected; is " + str(response['Content-Type'])
        if failtext != "":
            self.fail(failtext)
    
    def assertValidJSONResponse(self, response, contenttype='application/json'):
        failtext = ""
        try:
            json.loads(response.content)
        except ValueError:
            failtext = "Invalid JSON in response \n"
        if response['Content-Type'] != contenttype:
            failtext += "Content-Type header not " + contenttype + " as expected; is " + str(response['Content-Type'])
        if failtext != "":
            self.fail(failtext)
            
    def assertOKValidXML(self, response):
        self.assertValidXMLResponse(response)
        self.assertOKResponse(response)
        
    def assertOKValidJSON(self, response):
        self.assertValidJSONResponse(response)
        self.assertOKResponse(response)
        
    def assertResponse(self, response, expected):
        try:
            for response.status_code in expected:
                return
            fail('Status code ' + response.status_code + ' not among permitted values')
        except TypeError:
            self.assertEqual(response.status_code, expected)
   
    def assertOKResponse(self, response):
        self.assertResponse(response, status.OK)
        
