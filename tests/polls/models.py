# -*- coding: utf-8 -*-
""" Defines models for this sample project.
"""
from django.db import models


class Poll(models.Model):
#    choices = models.ManyToManyField(Choice)
    question = models.CharField('Poll Question', max_length=1024)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField()
    def __str__(self):
        return self.choice_text

