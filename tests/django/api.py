# -*- coding: utf-8 -*-
from armet import resources


class PollResource(resources.Resource):

    class Meta:
        connectors = {
            'http': 'django'
        }

    def read(self):
        return "Hello!"
