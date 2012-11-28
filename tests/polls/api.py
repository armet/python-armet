# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
from flapjack.resources import field, relation
from . import models
from flapjack.api import Api


class ChoiceWithPollExcluded(resources.Model):
    model = models.Choice
    resource_uri = None
    exclude = 'poll',


class Poll(resources.Model):

    model = models.Poll
    include = {
        'answers': field('choice_set'),
        'total_votes': field('choice_set')
    }

    relations = {
        'answers': relation(ChoiceWithPollExcluded, embed=True, local=True)
    }


    #TODO: Somebody please replace this with a faster sum function
    def prepare_total_votes(self,obj,val):
        votes = 0
        for i in val:
            votes += i.votes
        return votes

apiv6 = Api("v6")

apiv6.register(Poll)


#Issue #1:  inverse relationships cannot be accessed via API.

#Issue #2:  relations requires that the resource being linked to must have an exposed URL.  --fixed!

#Enhancement:  We should automatically create resources for models.
