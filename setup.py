#! /usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='armet',
    version='0.3.0-pre',
    description='Clean and modern framework for creating RESTful APIs.',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/armet/python-armet',
    package_dir={'armet': 'src/armet'},
    packages=find_packages('src'),
    install_requires=(
        'six', # Python 2 and 3 normalization layer
        'python-mimeparse' # For parsing accept and content-type headers
    ),
    extras_require={
        'test': (
            'nose',
            'yanc'
        )
    }
)
