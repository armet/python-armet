# -*- coding: utf-8 -*-
""" Defines models for this test project.
"""
from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=1024)
    pub_date = models.DateTimeField()


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=512)
    votes = models.IntegerField()
