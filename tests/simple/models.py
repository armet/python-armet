# -*- coding: utf-8 -*-
""" Defines models for this sample project.
"""
from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=1024)

    def __str__(self):
        return self.question
