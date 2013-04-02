# -*- coding: utf-8 -*-
from flask import Flask
import armet
from armet import resources

# Instantiate the flask application.
app = Flask(__name__)

@armet.route(app, '/api/')
class PollResource(resources.Resource):

    class Meta:
        connectors = {
            'http': 'flask'
        }

    def read(self):
        return "Hello!"

@armet.route(app, '/api/')
class HttpWholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        http_allowed_methods = ('GET', 'DELETE',)

@armet.route(app, '/api/')
class HttpForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        http_list_allowed_methods = ('DELETE',)
        http_detail_allowed_methods = ('GET',)

@armet.route(app, '/api/')
class WholeForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        allowed_operations = ('read', 'destroy',)

@armet.route(app, '/api/')
class ForbiddenResource(resources.Resource):

    class Meta:
        connectors = {'http': 'flask'}
        list_allowed_operations = ('destroy',)
        detail_allowed_operations = ('read',)

def main():
    # Run the application server.
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
