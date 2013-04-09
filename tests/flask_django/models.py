# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from django.db import models


class Poll(models.Model):

    question = models.CharField(max_length=1024)


class Choice(models.Model):

    text = models.CharField(max_length=1024)


class Vote(models.Model):

    ip_address = models.GenericIPAddressField()
