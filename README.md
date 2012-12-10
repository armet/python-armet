# Armet #
> Clean and modern framework for creating RESTful APIs.

## Dependencies ##
 - **python** `>= 2.7.x`
 - **django** `~= 1.4.x`

## Features ##
 - Adheres to all 4 constraints of the REST doctrine:
   - Identification of resources
   - Manipulation of resources through these representations
   - Self-descriptive messages
   - Hypermedia as the engine of application state (aka HATEOAS)

## Contributing ##

### Setting up your environment ###
The first thing you’re going to want to do, is build a virtual environment and install any base dependancies.
You'll want `virtualenvwrapper` which can be installed via `pip install virtualenvwrapper` if you don't 
already have it.

```sh
# Establish a new environment.
mkvirtualenv armet

# Ensure we are working on the established environment.
workon armet

# Install any and all base dependencies.
pip install -r requirements.txt
```

> **Note:**
> You'll need to install the build dependencies of `lxml` if you haven't already.
> That can be done via `sudo apt-get build-dep python-lxml` on debian-based distributions.

### Running the test suite ###
Running the test suite is simple as we're using both the django test client for its 
operations and nose for discovery.

```sh
# Ensure we are working on the established environment.
workon armet

# Instruct django to run the test suite located at src/armet/tests.
python manage.py test
```

## License ##
Unless otherwise noted, all files contained within this project are liensed
under the MIT opensource license. See the included file LICENSE or visit
[opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT
