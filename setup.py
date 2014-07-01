#! /usr/bin/env python
from setuptools import setup, find_packages
from imp import load_source


setup(
    name='armet',
    version=load_source('', 'armet/_version.py').__version__,
    description='Clean and modern framework for creating RESTful APIs.',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'Framework :: Flask',
        'Framework :: Django',
        # 'Framework :: CherryPy',
        # 'Framework :: Twisted',
        # 'Framework :: Pylons',
        # 'Framework :: Pyramid',
        # 'Framework :: SQLAlchemy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='http://github.com/armet/python-armet',
    packages=find_packages('.'),
    install_requires=[
        'pytest',  # Testing!
    ],
)
