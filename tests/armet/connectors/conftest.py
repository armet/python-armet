# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from armet import connectors


def pytest_generate_tests(metafunc):
    # Build a collection of connector hashes to represent every possible
    # arrangement.
    http = connectors.http
    model = connectors.model
    scenarios = [[{'http': x, 'model': y}] for x in http for y in model]
    ids = ['{}:{}'.format(x, y) for x in http for y in model]

    # Parameterize all test classes.
    metafunc.parametrize(['connectors'], scenarios, ids=ids, scope="class")
