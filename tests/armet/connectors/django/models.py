# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from django.db import models


class Poll(models.Model):

    question = models.CharField(max_length=1024)

    available = models.NullBooleanField()

    votes = models.IntegerField(null=True)
