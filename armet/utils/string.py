# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import re


def dasherize(value):
    """Dasherizes the passed value."""
    value = value.strip()
    value = re.sub(r'([A-Z])', r'-\1', value)
    value = re.sub(r'[-_\s]+', r'-', value)
    value = re.sub(r'^-', r'', value)
    value = value.lower()
    return value
