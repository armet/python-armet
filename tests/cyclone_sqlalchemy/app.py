# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from __future__ import absolute_import
from armet import resources
from armet.resources import attributes
from ..sqlalchemy import models
from cyclone import web


# Configure armet globally to use the appropriate connectors.
class Meta:
    connectors = {'http': 'cyclone', 'model': 'sqlalchemy'}


class SimpleResource(resources.ManagedResource):

    class Meta(Meta):
        pass

    def read(self):
        return None


class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll
        engine = models.engine

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


class HttpWholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


class HttpForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


class WholeForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


class ForbiddenResource(resources.ManagedResource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


# Export the cyclone application.
application = web.Application(debug=True)

# Mount the urls on the application.
mount = r'^/api'
SimpleResource.mount(mount, application)
PollResource.mount(mount, application)
HttpWholeForbiddenResource.mount(mount, application)
HttpForbiddenResource.mount(mount, application)
WholeForbiddenResource.mount(mount, application)
ForbiddenResource.mount(mount, application)
