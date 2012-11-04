#! /usr/bin/env python
import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
        name='flapjack',
        version=read('VERSION'),
        description='Clean and modern framework in django for creating '
                    'RESTful APIs.',
        long_description=read('README.md'),
        author='Concordus Applications',
        author_email='support@concordusapps.com',
        url='http://github.com/concordusapps/django-flapjack',
        package_dir={'flapjack': 'src/flapjack'},
        packages=find_packages('src')
    )
