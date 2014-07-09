from flask import Flask
from armet.api import Api
from armet.resources import Resource, prepares
from armet.http.exceptions import NotFound
from werkzeug.wsgi import DispatcherMiddleware
from datetime import datetime, timedelta

app = Flask(__name__)


class UserResource(Resource):

    # Data that this resource returns.
    users = [
        {
            'id': 1,
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'secret',
            'created_date': datetime.now() - timedelta(days=2),
        },
        {
            'id': 2,
            'username': 'joe',
            'email': 'joe@example.com',
            'password': 'hunter2',
            'created_date': datetime.now()
        }
    ]

    # All the attributes that will be returned when being read.
    attributes = {'id', 'username', 'email', 'created_date'}

    def read(self):
        # Implement slug based routing (/users/1 routes to a single one)
        if self.slug is None:
            # TODO: This is stupid.
            data = [type('StupidObject', (), x) for x in self.users]
        else:
            try:
                # Shoddy way of mapping ids to slugs (via array index.)
                slug = int(self.slug) - 1
            except ValueError as ex:
                raise NotFound() from ex

            if slug >= len(self.users) or slug < 0:
                raise NotFound()

            # TODO: This is stupid.
            data = type('StupidObject', (), self.users[slug])

        return data


@prepares(datetime)
def prepare_datetime(item, key, value):
    # Datetime objects are not inherently understood by many encoders
    # (xml being an exception)
    # so this function is in charge of normalizing the data into something
    # that can be understood by most encdoders.  Encoders will only
    # use this preparation function when they cannot inherantly encode
    # this format.
    return value.isoformat()


@app.route('/hello')
def flask_route():
    # Flask routes still work.
    return "Hello World!"


if __name__ == '__main__':
    # Create an api that can contain this resource.
    # Note that apis are valid wsgi applications, so we can mount/remount them
    # as we would any other wsgi application.
    api = Api()

    # Registering the resource within the application implicitly defines
    # a route to the resource.  The default route name is determined from the
    # class name (cls.__name__).  Take note of how capitalization maps:
    # * UserResource maps to '/user'
    # * MultiWordResource maps to '/user/multi-word'
    api.register(UserResource)

    # Create a new wsgi application based on the flask routes and mount our
    # armet api on /api
    application = DispatcherMiddleware(app, {
        '/api': api,
    })

    from werkzeug.serving import run_simple
    run_simple(
        '0.0.0.0', 5000, application,
        use_debugger=False,
        use_reloader=True)
