# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.conf.urls import patterns, include, url
from . import api

# URL configuration
urlpatterns = patterns(
    '',
    url(r'^api/', include(api.PollResource.urls)),
    url(r'^api/', include(api.SimpleResource.urls)),
    url(r'^api/', include(api.HttpWholeForbiddenResource.urls)),
    url(r'^api/', include(api.HttpForbiddenResource.urls)),
    url(r'^api/', include(api.WholeForbiddenResource.urls)),
    url(r'^api/', include(api.ForbiddenResource.urls)),
)
