#! /usr/bin/env python
import os
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read().strip()


setup(
        name='django-flapjack',
        version=read('VERSION'),
        description=read('description'),
        long_description=read('README.md'),
        author='Concordus Applications',
        author_email='support@concordusapps.com',
        url='http://github.com/concordusapps/django-flapjack',
        package_dir={'flapjack': 'src/flapjack'},
        packages=find_packages('src')
    )
