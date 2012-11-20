# -*- coding: utf-8 -*-
""" Defines forms for this sample project.
"""
from django import forms
from . import models


class Poll(forms.ModelForm):
    class Meta:
        model = models.Poll


class Choice(forms.ModelForm):
    class Meta:
        model = models.Choice
