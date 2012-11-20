# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from . import models

class Choice(resources.Model):
    #class Meta:
    model = models.Choice
    relations = {'poll': 'polls.api.Poll'}
#    name = 'answer'

class Poll(resources.Model):
    model = models.Poll
    relations = {'choice_set': 'polls.api.Choice'}
#    include = 'answers'

#    def prepare_answers(self,obj,value):
#         return [str(x) for x in obj.choice_set.all()]
#         return obj.choices.all()


#Issue #1:  inverse relationships cannot be accessed via API.

#Issue #2:  relations requires that the resource being linked to must have an exposed URL.

#Enhancement:  We should automatically create resources for models.
