# -*- coding: utf-8 -*-
"""Implements the encoder protocol for encoding an object into a JSON response.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from collections import Iterable, Mapping
import datetime
import yaml
import six
from .. import transcoders
from . import Encoder, utils


class Encoder(transcoders.Yaml, Encoder):

    def encode(self, obj=None):
        if isinstance(obj, datetime.time) or isinstance(obj, datetime.datetime):
            # This is some kind of date/time -- encode using ISO format.
            obj = obj.isoformat()

        # Encode and return the resultant text
        text = ''


        # text = yaml.dump(bytes(list(obj)), default_flow_style=True)

        print(obj)

        # Return our encoded result
        return yaml.dump(bytes(list(obj)), default_flow_style=True)
