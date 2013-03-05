# -*- coding: utf-8 -*-
""" Defines models for this test project.
"""
from django.db import models
from django.utils import timezone


class Poll(models.Model):
    question = models.CharField(max_length=1024)
    pub_date = models.DateTimeField()


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=512)
    votes = models.IntegerField()


class Booth(models.Model):
    name = models.CharField(max_length=1024)
    polls = models.ManyToManyField(Poll)

    @property
    def poll(self):
        return Poll(question=self.name, pub_date=timezone.now())


class Cushion(models.Model):
    color = models.CharField(max_length=1024)
    booth = models.ForeignKey(Booth)
