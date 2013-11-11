#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys
import platform


# Required test dependencies.
test_dependencies = (
    # Test runner.
    'pytest',

    # Ensure PEP8 conformance.
    'pytest-pep8',

    # Ensure test coverage.
    'pytest-cov',

    # Benchmarking.
    'pytest-bench',

    # Installs a WSGI application that intercepts requests made to a hostname
    # and port combination for testing.
    'wsgi_intercept == 0.6.0',

    # HTTP request abstraction layer over httplib.
    'httplib2',

    # The Web framework for perfectionists with deadlines.
    'django',

    # A microframework based on Werkzeug, Jinja2 and good intentions.
    'flask',

    # Bottle is a fast and simple micro-framework for small web applications.
    'bottle',

    # SQLAlchemy is the Python SQL toolkit and Object Relational Mapper
    # that gives application developers the full power and flexibility of SQL.
    'sqlalchemy',
)


if sys.version_info[0] == 2:
    if platform.python_implementation() != 'PyPy':
        # Test dependencies that don't apply for python 2.x.
        test_dependencies += (
            # gevent is a coroutine-based Python networking library that uses
            # greenlet to provide a high-level synchronous API on top of the
            # libevent event loop.
            'gevent',
        )


setup(
    name='armet',
    version='0.4.7',
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
        'python-mimeparse',
    ),
    extras_require={
        'test': test_dependencies
    }
)
