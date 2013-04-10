# -*- coding: utf-8 -*-
from flask import Flask
from ..django import models
import armet
from armet import resources
from armet.resources import attributes


# Instantiate the flask application.
application = Flask(__name__)


# Configure the flask application appropriately.
# NOTE: Flask does automatic removal of trailing slashes. If a user wishes
#   to use armet with `trailing_slash` set to `False` then the following
#   option must be turned off.
application.url_map.strict_slashes = False


class Meta:
    connectors = {
        'http': 'flask',
        'model': 'django'
    }


@armet.route(application, '/api/')
class SimpleResource(resources.Resource):

    class Meta(Meta):
        pass

    def read(self):
        return None


@armet.route(application, '/api/')
class PollResource(resources.ModelResource):

    class Meta(Meta):
        model = models.Poll

    id = attributes.Attribute('id')
    question = attributes.Attribute('question')


@armet.route(application, '/api/')
class HttpWholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_allowed_methods = ('GET', 'DELETE',)


@armet.route(application, '/api/')
class HttpForbiddenResource(resources.Resource):

    class Meta(Meta):
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)


@armet.route(application, '/api/')
class WholeForbiddenResource(resources.Resource):

    class Meta(Meta):
        allowed_operations = ('read', 'destroy',)


@armet.route(application, '/api/')
class ForbiddenResource(resources.Resource):

    class Meta(Meta):
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)


def main():
    # Run the application server.
    application.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
