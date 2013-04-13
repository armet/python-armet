# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
from armet import resources
# from armet.resources import attributes
# from ..sqlalchemy import models
from cyclone import web


# Configure armet globally to use the appropriate connectors.
class Meta:
    connectors = {'http': 'cyclone', 'model': 'sqlalchemy'}


class SimpleResource(resources.Resource):

    class Meta(Meta):
        pass

    def read(self):
        return None


# Export the cyclone application
application = web.Application(debug=True)

# Mount the urls on the application
SimpleResource.mount(r'^/api', application)
