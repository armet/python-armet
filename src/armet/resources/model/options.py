# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from importlib import import_module
from armet.exceptions import ImproperlyConfigured
from ..resource import options


class ModelResourceOptions(options.ResourceOptions):

    def __init__(self, meta, name, bases):
        # Initalize base resource options.
        super(ModelResourceOptions, self).__init__(meta, name, bases)

        if not self.connectors.get('model'):
            # Attempt to detect the model connector.
            self.connectors['model'] = options._detect_connector('model')
