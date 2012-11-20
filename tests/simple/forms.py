# -*- coding: utf-8 -*-
""" Defines forms for this sample project.
"""
from django import forms
from . import models


class Poll(forms.ModelForm):
    class Meta:
        # fields = ('question',)
        model = models.Poll

    # text = forms.MultipleChoiceField(('red', 'blue'), required=True)


# class Poll(forms.ModelForm):
#     class Meta:
#         model = models.Poll
#     blue = forms.CharField()
