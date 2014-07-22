#! /usr/bin/env python
from setuptools import setup, find_packages, Command
from imp import load_source
import subprocess


class PyTest(Command):
    # user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    user_options = []

    def initialize_options(self):
        # super().initialize_options()
        self.pytest_args = [
            '--verbose',
            '--pep8',
            '--cov', 'armet'
        ]

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'] + self.pytest_args)
        raise SystemExit(errno)


extras_require = {
    'test': [
        'SQLAlchemy'
    ]
}

# Note: Should be ordered in reverse dependency order (why?)
tests_require = [
    'pytest-pep8',
    'pytest-cov',
    'pytest-bench',
    'pytest',
]

setup(
    name='armet',
    version=load_source('', 'armet/_version.py').__version__,
    description='Clean and modern framework for creating RESTful APIs.',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        # 'Framework :: Bottle',
        # 'Framework :: Flask',
        # 'Framework :: Django',
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
        'ujson',
        'werkzeug',
        'python-mimeparse'
    ],
    cmdclass={'test': PyTest},
    extras_require=extras_require,
    tests_require=tests_require,
)
