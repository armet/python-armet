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

**Armet** exists as an abstraction layer above your
web server framework and therefore can run in most
frameworks and envrionments using connectors.

### Base

 - **[six](https://pypi.python.org/pypi/six)** — Python 2 and 3 compatibility utilities

### Connectors

 - **[django](https://www.djangoproject.com/)** — python `>= 2.6`, python `>= 3.2`
 - **[flask](http://flask.pocoo.org/)** — python `>= 2.6, < 3.0`

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
