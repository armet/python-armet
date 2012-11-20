# -*- coding: utf-8 -*-
""" Defines models for this sample project.
"""
from django.db import models


class Pizza(models.Model):
    poll = models.OneToOneField('simple.Poll')


class Hamburger(models.Model):
    polls = models.ManyToManyField('simple.Poll')


class Cheese(models.Model):
    poll = models.ForeignKey('simple.Poll')


class Booth(models.Model):
    name = models.CharField(max_length=1024)
    color = models.CharField(max_length=1024)
    booth = models.ForeignKey('self')

    def __str__(self):
        return self.name


class Poll(models.Model):
    question = models.CharField(max_length=1024)
    booths = models.ManyToManyField(Booth)
    polls = models.ManyToManyField('self')

    def __str__(self):
        return self.question
