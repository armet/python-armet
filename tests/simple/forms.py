# -*- coding: utf-8 -*-
""" Defines forms for this sample project.
"""
from django import forms
from . import models


class Poll(forms.Form):
    question = forms.CharField()
    booths = forms.MultipleChoiceField((1, 2, 3, 4, 5))


# class Poll(forms.ModelForm):
#     class Meta:
#         model = models.Poll
#     blue = forms.CharField()
