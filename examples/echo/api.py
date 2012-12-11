# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from armet import http
from armet import resources
from armet.resources import field, relation


class Echo(resources.Resource):

    def prepare(self, data):
        # Nop out the preparation cycle
        return data

    def post(self, data):
        # Return the response
        return data, http.client.OK
