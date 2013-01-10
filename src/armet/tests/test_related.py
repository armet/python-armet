# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http
from armet.utils import test
from armet import resources, encoders
from django import forms
from django.db import models


class RelatedTest(test.TestCase):

    def test_property(self):

        class TeamModel(models.Model):
            name = models.CharField(max_length=30)
            resource_uri = None

        class UserModel(models.Model):
            first_name = models.CharField(max_length=30)
            last_name = models.CharField(max_length=30)

            @property
            def team(self):
                return TeamModel(name=self.first_name)

        class TeamResource(resources.Model):
            model = TeamModel

        class UserResource(resources.Model):
            model = UserModel
            resource_uri = None
            include = {
                'team': resources.attribute('team')
            }

            relations = {
                'team': resources.relation(TeamResource, path='name', embed=True)
            }

        request = RequestFactory().get('/property/5')
        resource = UserResource(request=request, slug=5)
        data = resource.prepare(UserModel(first_name="Bob", last_name="Smith"))

        self.assertEquals(data['team'], 'Bob')
