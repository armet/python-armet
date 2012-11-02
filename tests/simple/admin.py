# -*- coding: utf-8 -*-
""" Registers the models with the administration interface.
"""
from django.contrib.admin import site
from . import models


site.register(models.Poll)
