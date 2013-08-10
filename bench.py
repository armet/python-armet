#! /usr/bin/env python
from tests import conftest
from tests.armet.connectors import sqlalchemy as models
import armet
from armet import resources
from flask import Flask
import wsgi_intercept
from wsgi_intercept.httplib2_intercept import install
import requests
import timeit
import httplib2


app = Flask(__name__)

armet.use(connectors={'http': 'flask', 'model': 'sqlalchemy'},
          debug=False,
          Session=models.Session)


HOST = 'localhost'

PORT = 5000


@armet.route('/', app)
class PollResource(resources.ModelResource):

    class Meta:
        model = models.Poll

        slug = resources.IntegerAttribute('id')

    id = resources.IntegerAttribute('id')

    question = resources.TextAttribute('question')

    available = resources.BooleanAttribute('available')


def bench_full_request():
    con = httplib2.Http()
    response, content = con.request('http://%s:%s/poll' % (HOST, PORT), 'GET')


def setup_session():
    install()
    wsgi_intercept.add_wsgi_intercept(HOST, PORT, lambda: app)
    models.model_setup()


def teardown_session():
    wsgi_intercept.remove_wsgi_intercept(HOST, PORT)


def main():
    setup_session()
    time = timeit.timeit(bench_full_request, number=1000) / 1000
    print(time)
    teardown_session()


if __name__ == '__main__':
    main()
