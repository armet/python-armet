# from django.test import TestCase
# from django.test.client import RequestFactory


class Base(object):

    fixtures = ['inital_data']

    @property
    def path(self):
        return "/api/{}".format(self.name)

    def get(
            self,
            path,
            accept='application/json'):
        return self.client.get(path, HTTP_ACCEPT=accept)
