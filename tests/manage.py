#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
import sys
from django.core.management import execute_from_command_line


if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))

    execute_from_command_line(sys.argv)
