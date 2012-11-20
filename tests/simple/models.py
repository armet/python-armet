# -*- coding: utf-8 -*-
""" Defines models for this sample project.
"""
from django.db import models


class Booth(models.Model):
    name = models.CharField(max_length=1024)
    color = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


class Poll(models.Model):
    question = models.CharField(max_length=1024)
    # booths = models.ManyToManyField(Booth, blank=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    text = models.CharField(max_length=1024)

    def __str__(self):
        return self.text
