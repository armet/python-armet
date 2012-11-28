# -*- coding: utf-8 -*-
""" Defines models for this sample project.
"""
import datetime
from django.db import models
from django.utils import timezone


class Booth(models.Model):
    name = models.CharField(max_length=512)


class Poll(models.Model):
    question = models.CharField(max_length=1024)
    pub_date = models.DateTimeField('date published')
    booths = models.ManyToManyField(Booth)

    @property
    def published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    @property
    def forty_two(self):
        return 42

    def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=1024)
    votes = models.IntegerField()

    def __str__(self):
        return self.choice_text
