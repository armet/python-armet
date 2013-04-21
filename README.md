# python-armet [![Build Status](https://travis-ci.org/armet/python-armet.png)](https://travis-ci.org/armet/python-armet)
> Clean and modern framework for creating RESTful APIs.

**Armet** is a framework to facilitate the **quick** **creation**
of **fast**, **powerful**, and **conformant** **REST**ful application
programming interfaces. Developing a RESTful API should not be something
that is time consuming or difficult; it should at least not be something
that takes more time to develop then its underlying functionality. **Armet**
enables you, the developer, to focus on developing the application
behind the interface.

## Prerequisites

###### [six](https://pypi.python.org/pypi/six) `~ 0.1.3`
> Python 2 and 3 compatibility utilities.

###### [mimeparse](https://pypi.python.org/pypi/python-mimeparse/) `~ 0.1.4`
> A module provides basic functions for parsing mime-type names and 
> matching them against a list of media-ranges.

###### [gevent](http://www.gevent.org/) `~ 1.0` *optional*
> A coroutine-based Python networking library that uses greenlet to provide 
> high-level synchronous API on top of the libevent event loop.

Provides tight integration for WSGI-based connectors with gevent so a request
may be transparently handled asynchronously. The code snippet below demonstates
this with the **bottle** connector however any WSGI-based connector
could be used (eg. **django**, **flask**, etc.).

```python
import gevent
from gevent import monkey
monkey.patch_all()  # Transparently switch python to use gevent.
   
from bottle import run
from armet import resources, route
import time
   
@route('/')
class Resource(resources.Resource):
    class Meta:
        connectors = {'http': 'bottle'}
        asynchronous = True
   
    def get(self):
        def writer(index, delay):
            for number in range(10):
                self.response.write('{}: {}\n'.format(index, number))
                time.sleep(delay)  # Wait a bit so we can see it streaming.
                self.response.flush()  # Async write body to transport stream.
                
        def spawner():
            threads = []  # Initialize a thread group
            for index in range(10):
                # Spawn lots of writer jobs with various delays.
                threads.append(gevent.spawn(writer, index, index / 10))
            
            gevent.joinall(threads)  # Wait for all threads to finish
            self.response.close()  # Close the http connection.
            
        gevent.spawn_later(1, spawner)  # Spawn the spawner after a second for fun
   
run(server='gevent')
```

Non WSGI-based connectors provide an identical interface to write to the 
response stream asynchronously (eg. **twisted**).

## Connectors

**Armet** exists as an abstraction layer above your
web server framework and therefore can run in most
frameworks and envrionments using connectors.

There are two kinds of connectors: `http` and `model`. The `http` connector
is in charge of facilitating the request / response cycle. The `model`
connector is in charge of facilitating the database access layer for RESTful
resources that are bound to a declarative model. For the most part these
connectors can be mixed and changed at a per-resource level (eg. one resource
may use `django` for its http connector and `sqlalchemy` for its model
and another may still use `django` for its http connector but reuse it for
its model one as well).

### Request / response (http)

###### [Django](https://www.djangoproject.com/) `>= 1.4`
> The Web framework for perfectionists (with deadlines).
> Django makes it easier to build better Web apps more quickly and
> with less code.

```python
# api.py
from armet import resources
class Resource(resources.Resource):
    class Meta:
        connectors = {
            'http': 'django',
            # ... [additional connectors]
        }

# urls.py
# ... [appending to the generated urls.py file from django-admin.py startproject]
from . import api
urlpatterns += patterns('',
    url(r'^api/', include(api.Resource.urls)),
)
```

###### [Flask](http://flask.pocoo.org/)
> Flask is a microframework for Python based on Werkzeug,
> Jinja 2 and good intentions.

```python
# Initialize the flask application.
from flask import Flask
app = Flask(__name__)

import armet
from armet import resources

@armet.route(app, '/api/')
class Resource(resources.Resource):
    class Meta:
        connectors = {
            'http': 'flask',
            # ... [additional connectors]
        }
```

###### [Bottle](http://bottlepy.org/docs/dev/)
> Bottle is a fast, simple and lightweight 
> WSGI micro web-framework for Python.

```python
from armet import resources, route

@route('/api/')
class Resource(resources.Resource):
    class Meta:
        connectors = {
            'http': 'bottle',
            # ... [additional connectors]
        }
```

###### [Cyclone](http://cyclone.io/)
> Cyclone is a web server framework for Python that implements 
the Tornado API as a Twisted protocol.

```python
from armet import resources, route

# Mount the resource using the 
# bottle-style application
@route(r'/api')
class Resource(resources.Resource):
    class Meta:
        connectors = {
            'http': 'cyclone',
            # ... [additional connectors]
        }

from cyclone import web
application = web.Application([
  # Mount the resource in the application 
  # constructor directly
  (r'^/api/{}(.*)'.format(Resource.meta.name), Resource.handler),
  
  # Mount the resource in the application
  # constructor using a helper
  Resource.route(r'^/api'), #=> (r'^/api/resource(.*)', Resource.handler)
])

# Mount the resource on the cyclone application.
Resource.mount(r'^/api', application)
```

### Database access (model)

###### [Django](https://www.djangoproject.com/) `>= 1.4`
> The Web framework for perfectionists (with deadlines).
Django makes it easier to build better Web apps more quickly and with less code.

###### [SQLAlchemy](http://www.sqlalchemy.org/) `>= 0.7`
> SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that 
gives application developers the full power and flexibility of SQL.

## Installation

### Automated

1. **Armet** is not yet listed on [PyPI](https://pypi.python.org/pypi/)
   but can be installed by directly referencing its git url with `pip`
   or `easy_install`.

   ```sh
   pip install git+git://github.com/armet/python-armet.git
   ```

   > Examples are not included when installing using `pip` or `easy_install`.

### Manual

1. Clone the **Armet** repository to your local computer.

   ```sh
   git clone git://github.com/armet/python-armet.git
   ```

   To grab a specific version you can use the `-b` argument to specify
   a branch, which can include a specific tag
   as well (eg. `versions/0.4.x` or `0.4.1`).

   ```sh
   git clone -b 0.3.1 git://github.com/armet/python-armet.git
   ```

   To speed up the clone if you're just cloning the project for use and
   don't intend to contribute back upstream, you can add the `--depth `
   option to do a shallow clone, in which it will only fetch the
   exact version instead of the entire history.

   ```sh
   git clone -b 0.3.1 --depth 1 git://github.com/armet/python-armet.git
   ```

2. Change into the **armet** root directory.

   ```sh
   cd /path/to/python-armet
   ```

3. Install the project and all its dependencies using `pip`.

   ```sh
   pip install .
   ```

   Additional *extra* requirements may be specified in brackets following
   the `.`.

   ```sh
   # Install armet as well as the additional dependencies to use
   # the unit test suite.
   pip install ".[test]"
   ```

## Contributing

### Setting up your environment
1. Follow steps 1 and 2 of the [manual installation instructions][].

[manual installation instructions]: #manual

2. Initialize a virtual environment to develop in.
   This is done so as to ensure every contributor is working with
   close-to-identicial versions of packages.

   ```sh
   mkvirtualenv armet
   ```

   The `mkvirtualenv` command is available from `virtualenvwrapper` which
   can be installed as follows:

   ```sh
   sudo pip install virtualenvwrapper
   ```

3. Install **armet** in development mode with testing enabled.
   This will download all dependencies required for running the unit tests.

   ```sh
   pip install -e ".[test]"
   ```

### Running the test suite
1. [Set up your environment](#setting-up-your-environment).

2. Run the unit tests.

   ```sh
   nosetests
   ```

**Armet** is maintained with all tests passing at all times. If you find
a failure, please [report it](https://github.com/armet/python-armet/issues/new)
along with the version.

## License
Unless otherwise noted, all files contained within this project are liensed
under the MIT opensource license. See the included file LICENSE or visit
[opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT
