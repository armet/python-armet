#! /usr/bin/env python
from setuptools import setup, find_packages
import sys


#! True if we are running on Python 3.
PY3 = sys.version_info[0] == 3


# Required test dependencies.
test_dependencies = (
    # Test runner.
    'nose',

    # Colorized output for the test runner.
    'yanc',

    # Installs a WSGI application in place of a real URI for testing.
    'wsgi_intercept == 0.6.0',

    # HTTP request abstraction layer over httplib.
    'httplib2',

    # The Web framework for perfectionists with deadlines.
    'django',
)


if not PY3:
    # Test dependencies for python 2.x only.
    test_dependencies += (
        # A microframework based on Werkzeug, Jinja2 and good intentions.
        'flask',
    )


setup(
    name='armet',
    version='0.3.0-pre',
    description='Clean and modern framework for creating RESTful APIs.',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/armet/python-armet',
    package_dir={'armet': 'src/armet'},
    packages=find_packages('src'),
    dependency_links=(
        'git+git://github.com/concordusapps/wsgi-intercept.git'
        '#egg=wsgi_intercept-0.6.0',
    ),
    install_requires=(
        # Python 2 and 3 normalization layer
        'six',

        # For parsing accept and content-type headers
        'python-mimeparse'
    ),
    extras_require={
        'test': test_dependencies
    }
)
