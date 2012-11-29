# -*- coding: utf-8 -*-
""" Defines the root URL configuration.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import server
from . import api as resources

from flapjack import api

api = api.Api()
api.register(resources.Poll)
# api.register(resources.Choice)

# Execute the server startup sequence
server.startup()

# URL configuration
urlpatterns = patterns('',
    # Administration
    url(r'^admin/', include(admin.site.urls)),

    # Resources
    url(r'^api/', include(api.urls))
)
