# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sys
from armet import resources

# Request the generic models module inserted by the test runner.
models = sys.modules['tests.connectors.models']

__all__ = [
    'SimpleResource',
    'PollResource'
]


class SimpleResource(resources.Resource):

    def get(self):
        # Do nothing and return nothing.
        pass


class PollResource(resources.ModelResource):

    class Meta:
        model = models.Poll

        slug = resources.IntegerAttribute('id')

    id = resources.IntegerAttribute('id')

    question = resources.TextAttribute('question')
