# -*- coding: utf-8 -*-
from flask import Flask
import armet
from armet import resources


# Instantiate the flask application.
application = Flask(__name__)


# Configure the flask application appropriately.
# NOTE: Flask does automatic removal of trailing slashes. If a user wishes
#   to use armet with `trailing_slash` set to `False` then the following
#   option must be turned off.
application.url_map.strict_slashes = False


# Mount our resources manually.
# We could do @armet.route(application, '/api/')
# We should propbably test that method.
from tests.flask_django import api
api.PollResource.mount(application, '/api/')
api.SimpleResource.mount(application, '/api/')
api.HttpWholeForbiddenResource.mount(application, '/api/')
api.HttpForbiddenResource.mount(application, '/api/')
api.WholeForbiddenResource.mount(application, '/api/')
api.ForbiddenResource.mount(application, '/api/')


def main():
    # Run the application server.
    application.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
