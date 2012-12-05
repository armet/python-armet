#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
import sys
from django.core.management import execute_from_command_line


if __name__ == "__main__":
    sys.path.append(os.path.join('src'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flapjack.tests.settings")
    execute_from_command_line(sys.argv)
