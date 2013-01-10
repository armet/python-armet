# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http
from armet.utils import test
from armet import resources
from django import forms
from django.db import models


class FieldTest(test.TestCase):

    def test_generic_ip_address(self):
        try:
            class GenericIPResource(resources.Model):
                class model(models.Model):
                    ip_address = models.GenericIPAddressField()

        except BaseException as ex:
            self.fail(ex)
