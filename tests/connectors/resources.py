# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import resources


class SimpleResource(resources.Resource):

    def get(self):
        # Do nothing and return nothing.
        pass
