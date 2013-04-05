# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
import re
import collections
import os
import pkgutil
import importlib
import functools


def dasherize(value):
    """Dasherizes the passed value."""
    value = value.strip()
    value = re.sub(r'([A-Z])', r'-\1', value)
    value = re.sub(r'[-_\s]+', r'-', value)
    value = re.sub(r'^-', r'', value)
    value = value.lower()
    return value
