# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http
from armet.utils import test
from armet import resources, encoders
from django import forms
from django.db import models
from . import models as local_models


class RelatedTest(test.TestCase):

    def setUp(self):
        self.booth = local_models.Booth.objects.create(name="Steve")
        self.booth.polls.add(5)
        self.booth.polls.add(15)

    def test_property(self):

        class TeamModel(models.Model):
            name = models.CharField(max_length=30)

        class UserModel(models.Model):
            first_name = models.CharField(max_length=30)
            last_name = models.CharField(max_length=30)

            @property
            def team(self):
                return TeamModel(name=self.first_name)

        class TeamResource(resources.Model):
            model = TeamModel
            resource_uri = None
            canonical = False

        class UserResource(resources.Model):
            model = UserModel
            canonical = False
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

    def test_many_to_many(self):

        class BoothResource(resources.Model):
            model = local_models.Booth
            canonical = False
            resource_uri = None

        request = RequestFactory().get('/booth/1')
        resource = BoothResource(request=request, slug=1)
        data = resource.prepare(self.booth)

        self.assertEquals(data['polls'][0], "/poll/5")
        self.assertEquals(data['polls'][1], "/poll/15")

        # request = RequestFactory().get('/property/5')
        # resource = UserResource(request=request, slug=5)
        # user = UserModel(first_name="Bob", last_name="Smith")
        # user.id = 2
        # user.teams.add(TeamModel(id=32, name="Steve"))

        # data = resource.prepare()

        # self.assertEquals(data['team'], 'Bob')
