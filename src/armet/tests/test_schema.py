# -*- coding: utf-8 -*-
from armet.utils import test
from armet.tests import api


class SchemaTestCase(test.TestCase):

    # TODO: test_json
    # TODO: test_xml

    def test_yaml(self):
        print(api.Poll.schema('yaml'))
        # TODO: Actually assert that we get a proper schema
