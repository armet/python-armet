# -*- coding: utf-8 -*-
""" WSGI configuration file.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
from django.core.wsgi import get_wsgi_application
from .settings import PROJECT_NAME


settings = "{}.settings".format(PROJECT_NAME)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

application = get_wsgi_application()
