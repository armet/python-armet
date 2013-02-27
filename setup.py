#! /usr/bin/env python
import os
import re
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read().strip()


def read_requirements(name):
    filename = 'doc/requirements/{}.txt'.format(name)
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        result = []
        for line in file.readlines():
            result.append(re.match(r'^(.*?)#|$', line).groups()[0].strip())
        return result


setup(
    name='armet',
    version='0.3.0-pre',
    description='Clean and modern framework for creating RESTful APIs.',
    long_description=read('README.md'),
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/armet/python-armet',
    package_dir={'armet': 'src/armet'},
    packages=find_packages('src'),
    install_requires=read_requirements('required'),
    extras_require={
        'test': read_requirements('test'),
    }
)
