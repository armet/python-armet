# -*- coding: utf-8 -*-
""" Defines the RESTful interface for this sample project.
"""
from flapjack import resources
# from flapjack.resources import relation, field
# from . import forms
# from django import forms
from . import forms, models

# from .forms
# class Form(forms.ModelForm):

#     class Meta:
#         model = models.Poll


class Choice(resources.Model):
    form = forms.Choice

    def read(self):
        return models.Choice.objects.all().iterator()


class Poll(resources.Model):
    form = forms.Poll

    def read(self):
        return models.Poll.objects.all().iterator()

# form = forms.Poll

# relations = {
#     'user': relation('account.User', path='username', embed=True),
#     'dog': relation('animal.Dog', path='name')
# }

# exclude = ('password', 'user', 'first_name', 'last_name')

# include = {
#     'dog': field('user__dog')
# }
