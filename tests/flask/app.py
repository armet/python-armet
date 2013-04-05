# -*- coding: utf-8 -*-
from flask import Flask
import armet
from armet import resources


# Instantiate the flask application.
application = Flask(__name__)


@armet.route(application, '/api/')
class SimpleResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}


@armet.route(application, '/api/')
class HttpWholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        http_allowed_methods = ('GET', 'DELETE',)


@armet.route(application, '/api/')
class HttpForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


@armet.route(application, '/api/')
class WholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        allowed_operations = ('read', 'destroy',)


@armet.route(application, '/api/')
class ForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


def main():
    # Run the application server.
    application.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
