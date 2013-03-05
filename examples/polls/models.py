# -*- coding: utf-8 -*-
""" Defines models for this test project.
"""
from django.db import models
from django.db.models import Q
from django.utils import timezone
import shield


@shield.rules
class Poll(models.Model):
    question = models.CharField(max_length=1024)
    pub_date = models.DateTimeField()

    @shield.rule('read')
    def can_read(cls, user):
        return Q(pk=user.pk)
