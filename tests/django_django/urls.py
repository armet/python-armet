# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.conf.urls import patterns, include, url
from . import api

# URL configuration
urlpatterns = patterns(
    '',
    url(r'^api/', include(api.PollResource.urls)),
    url(r'^api/', include(api.StreamingResource.urls)),
    url(r'^api/', include(api.SimpleResource.urls)),
    url(r'^api/', include(api.AsyncResource.urls)),
    url(r'^api/', include(api.AsyncStreamResource.urls)),
    url(r'^api/', include(api.HttpWholeForbiddenResource.urls)),
    url(r'^api/', include(api.HttpForbiddenResource.urls)),
    url(r'^api/', include(api.WholeForbiddenResource.urls)),
    url(r'^api/', include(api.ForbiddenResource.urls)),
)
