# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.conf.urls import patterns, include, url
from ..utils import force_import_module


# Initial URL configuration.
urlpatterns = patterns('')

# Import the resources; iterate and mount each one.
module = force_import_module('tests.connectors.resources')
for name in module.__all__:
    cls = getattr(module, name)
    urlpatterns += patterns('', url(r'^api/', include(cls.urls)))
