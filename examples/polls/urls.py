# -*- coding: utf-8 -*-
""" Defines the root URL configuration.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from django.conf.urls import patterns, include, url
from django.contrib import admin
from armet.api import Api
from . import api


# Discover administration modules
admin.autodiscover()

# Collect API endpoints
# TODO: Replace with interface.autodiscover('polls')
interface = Api()
interface.register(api.Choice)
interface.register(api.Poll)


# URL configuration
urlpatterns = patterns('',
    # Administration
    url(r'^admin/', include(admin.site.urls)),

    # Application interface
    url(r'^', include(interface.urls)),
<<<<<<< HEAD

    # url(^'api2/', include(api.Poll.urls)),
=======
>>>>>>> 7c420c3dbb2dbbb2678d8f5398e0e249c8cdd4e5
)
