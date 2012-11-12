# -*- coding: utf-8 -*-
""" Defines the root URL configuration.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.conf.urls import patterns, include, url
from django.contrib import admin
from . import server, api


# Execute the server startup sequence
server.startup()

# URL configuration
urlpatterns = patterns('',
    # Administration
    url(r'^admin/', include(admin.site.urls)),

    # Resources
    url(r'^api/', include(api.Poll.urls)),
    url(r'^api/', include(api.Booth.urls))
)
