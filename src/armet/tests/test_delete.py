# -*- coding: utf-8 -*-
# import hashlib
from armet import http#, exceptions
from armet.utils import test
# from armet import resources, encoders
# from django import forms
# from django.db import models
from . import models as local_models
# import six
# from armet.resources import Resource


class DeleteTest(test.TestCase):

    fixtures = ['initial_data']

    def setUp(self):
        super(DeleteTest, self).setUp()
        self.poll = local_models.Poll.objects.create(
            question="Why???How????When????",
            pub_date='1988-10-08T10:11:12+01:00'
        )
        self.choice_one = local_models.Choice.objects.create(
            poll=self.poll,
            choice_text="Because...",
            votes=5
        )
        self.booth = local_models.Booth.objects.create(name="Steve")

    def test_delete_success(self):
        urls = ('/poll/{}'.format(self.poll.id),
                '/answers/{}'.format(self.choice_one.id))
        url = urls[0] + urls[1]
        for x in urls:
            response = self.client.delete(url)
            self.assertHttpStatus(response, http.client.NO_CONTENT)
            response = self.client.get(url)
            self.assertHttpStatus(response, http.client.NOT_FOUND)
            url = urls[0]

    def test_delete_fail(self):
        url = '/poll/{}'.format(self.poll.id + 42)
        response = self.client.delete(url)
        self.assertHttpStatus(response, http.client.NOT_FOUND)

    def test_delete_whole_resource(self):
        urls = ('/choice/', '/poll/', '/booth_somethign_else_blah_blah/')
        for url in urls:
            response = self.client.delete(url)
            self.assertHttpStatus(response, http.client.NO_CONTENT)
            response = self.client.get(url)
            self.assertHttpStatus(response, http.client.OK)
            self.assertEqual(len(response.content), 2)
