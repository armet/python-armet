# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.conf.urls import patterns, include, url
from importlib import import_module
from armet import resources


# Initial URL configuration.
urlpatterns = patterns('')

# Import the resources; iterate and mount each one.
for cls in import_module('tests.connectors.resources').__dict__.values():
    if isinstance(cls, type) and issubclass(cls, resources.Resource):
        urlpatterns += patterns('', url(r'^api/', include(cls.urls)))
