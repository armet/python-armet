#! /usr/bin/env bash
# TODO: Get a better test runner

export PYTHONPATH="${PWD}"
export DJANGO_SETTINGS_MODULE="simple.settings"
admin=`which django-admin.py`
python2 $admin test simple
