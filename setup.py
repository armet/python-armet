#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys


#! True if we are running on Python 3.
PY3 = sys.version_info[0] == 3


# Required test dependencies.
test_dependencies = (
    # Test runner.
    'nose',

    # Run various test configurations against a single package of tests.
    'nose-interface',

    # Colorized output for the test runner.
    'yanc',

    # Installs a WSGI application in place of a real URI for testing.
    'wsgi_intercept == 0.6.0',

    # HTTP request abstraction layer over httplib.
    'httplib2',

    # The Web framework for perfectionists with deadlines.
    'django',

    # Django Extensions is a collection of custom extensions for the
    # Django Framework.
    'django-extensions',

    # Bottle is a fast and simple micro-framework for small web applications.
    'bottle',
)


if not PY3:
    # Test dependencies for python 2.x only.
    test_dependencies += (
        # A microframework based on Werkzeug, Jinja2 and good intentions.
        'flask',
    )


if sys.version_info[0] == 2 or sys.version_info[1] < 3:
    test_dependencies += (
        # A library for testing in Python. It allows you to replace
        # parts of your system under test with mock objects and make
        # assertions about how they have been used.
        # NOTE: Mock is now part of the standard library (>= 3.3) but
        #   armet supports python 2.x and python 3.2 so we include this library
        #   if our user is not in python 3.3.
        'mock',
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
        'git+git://github.com/concordusapps/nose-interface.git'
            '#egg=nose-interface-0.1.0'
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
