# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
# from flapjack.resources import relation, field
# from . import forms
# from django import forms
from . import models

# from .forms
# class Form(forms.ModelForm):

#     class Meta:
#         model = models.Poll


class Poll(resources.Model):
    model = models.Poll
    http_method_names = 'get',


class Booth(Poll):
    model = models.Booth
    pass

# form = forms.Poll

# relations = {
#     'user': relation('account.User', path='username', embed=True),
#     'dog': relation('animal.Dog', path='name')
# }

# exclude = ('password', 'user', 'first_name', 'last_name')

# include = {
#     'dog': field('user__dog')
# }
