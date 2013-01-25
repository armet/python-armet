# -*- coding: utf-8 -*-
""" Defines base project settings.
"""
# from __future__ import print_function, unicode_literals
# from __future__ import absolute_import, division
from os import path


# Project directories
PROJECT_NAME = 'polls'
PROJECT_ROOT = path.abspath(path.join(__file__))

# Root directories
SITE_ROOT = path.abspath(path.join(PROJECT_ROOT, '..'))

# Debugging settings
DEBUG = True

# Debug templates with all the nice stack traces
TEMPLATE_DEBUG = DEBUG

# Forces debugging to false if server is accessed from an IP not listed here
INTERNAL_IPS = ('127.0.0.1', '::1',)

# Site administrators; used for logging
ADMINS = ()

# Same as ADMINS but in a different group
MANAGERS = ADMINS

# Database configuration.
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': path.join(SITE_ROOT, 'db.sqlite'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}}

# Local time zone for this installation.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = path.join(SITE_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = ''

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '58yno^b5t^wvr)e4s8tet4&amp;#odp+9@+tu*nrq#*#d*gds%06w+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Middleware classes
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Root URL configuration
ROOT_URLCONF = '{}.urls'.format(PROJECT_NAME)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '{}.wsgi.application'.format(PROJECT_NAME)

# Installed applications
INSTALLED_APPS = (
    # Django core
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django administration
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Extensions
    'django_extensions',

    # Project
    PROJECT_NAME,

    # Test runner
    'devserver'
)

DEVSERVER_TRUNCATE_SQL = False

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'armet': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'filters': []
        },
    }
}
