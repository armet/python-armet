# -*- coding: utf-8 -*-
from flask import Flask
import armet
from armet import resources

# Instantiate the flask application.
app = Flask(__name__)

@armet.route(app, '/api/')
class PollResource(resources.Resource):

    def read(self):
        return "Hello!"

def main():
    # Run the application server.
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    main()
