# -*- coding: utf-8 -*-
import hashlib
from django.test.client import RequestFactory
from armet import http, exceptions
from armet.utils import test
from armet import resources, encoders
from django import forms
from django.db import models
from . import models as local_models
import six


class RelatedTest(test.TestCase):

    def setUp(self):
        self.booth = local_models.Booth.objects.create(name="Steve")
        self.booth.polls.add(5)
        self.booth.polls.add(15)

    def test_property(self):
        class HatModel(models.Model):
            name = models.CharField(max_length=30)

        class TeamModel(models.Model):
            name = models.CharField(max_length=30)

            @property
            def hat(self):
                return HatModel(name=self.name)

        class UserModel(models.Model):
            first_name = models.CharField(max_length=30)
            last_name = models.CharField(max_length=30)
            team = models.OneToOneField(TeamModel)

        class HatResource(resources.Model):
            model = HatModel
            resource_uri = None

        class UserResource(resources.Model):
            model = UserModel
            resource_uri = None
            exclude = ('team',)
            include = {
                'hat': resources.attribute('team__hat')
            }

            relations = {
                'hat': resources.relation(HatResource)
            }

        request = RequestFactory().get('/property/5')
        resource = UserResource(request=request, slug=5)

        model = UserModel(
            first_name="Bob", last_name="Smith",
            team=TeamModel(name='George'))

        data = resource.prepare(model)

        self.assertIs(data['hat'], six.string_types)

        # self.assertEquals(data['team'], 'Bob')

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

    def test_missing_resource(self):
        try:
            class AppleModel(models.Model):
                name = models.CharField(max_length=30)

            class FruitModel(models.Model):
                apple = models.ManyToManyField(AppleModel)

            class FruitResource(resources.Model):
                model = FruitModel
                canonical = False
                resource_uri = None

            request = RequestFactory().get('/fruit/1')
            resource = FruitResource(request=request, slug=1)
            data = resource.prepare({'apple': 3})

        except exceptions.NotFound:
            pass

        except:
            self.fail()
