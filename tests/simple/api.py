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


# class Choice(resources.Model):
#     form = forms.Choice


class Choice(resources.Model):
    model = models.Choice

    include = {
        'name_twice': resources.field('text'),
        'name_upper': resources.field('text'),
    }

    def prepare_name_upper(self, obj, value):
        return value.upper()

# class Booth(resources.Resource):

#     include = {
#         'id': resources.field(),
#         'name': resources.field(),
#         'other': resources.field('name'),
#     }

#     @classmethod
#     def slug(cls, obj):
#         return obj['id']

#     def prepare_name(self, obj, value):
#         return value.upper()

#     def read(self):
#         results = []
#         for x in range(1, 50):
#             results.append({
#                 'id': x,
#                 'name': "This is not a random name"
#             })
#         return results

# form = forms.Poll

# relations = {
#     'user': relation('account.User', path='username', embed=True),
#     'dog': relation('animal.Dog', path='name')
# }

# exclude = ('password', 'user', 'first_name', 'last_name')

# include = {
#     'dog': field('user__dog')
# }
