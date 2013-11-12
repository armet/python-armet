# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six
import unittest
from armet import resources
from pytest import mark


# @mark.bench('self.Resource.parse', iterations=10000)
@mark.bench('self.request', iterations=10000)
class ParseTestCase(unittest.TestCase):

    def setUp(self):
        super(ParseTestCase, self).setUp()

        # Construct a resource.
        class Resource(resources.ManagedResource):
            class Meta:
                abstract = True

        # Store the resource
        self.Resource = Resource

    def request(self, url):
        # Execute the parse method.
        _, arguments, _ = self.Resource.parse(url)

        # Assert that we got enough of them.
        assert 'slug' in arguments
        assert 'query' in arguments
        assert 'extensions' in arguments
        assert 'directives' in arguments
        assert 'path' in arguments

        # Return the arguments
        return arguments

    def assert_arguments(self, arguments, **kwargs):
        for argument in kwargs:
            value = arguments.pop(argument)
            assert value == kwargs[argument]

        for name, value in six.iteritems(arguments):
            test = [] if name.endswith('s') else None
            assert value == test

    def test_simple(self):
        arguments = self.request('/')

        self.assert_arguments(arguments)

    def test_slug(self):
        arguments = self.request('/123/')

        self.assert_arguments(arguments, slug='123')

    def test_slug_long(self):
        arguments = self.request('/sdf-sdg-sgh-sh234-bf/')

        self.assert_arguments(arguments, slug='sdf-sdg-sgh-sh234-bf')

    def test_query(self):
        arguments = self.request('(stuff=32)/')

        self.assert_arguments(arguments, query='stuff=32')

    def test_query_long(self):
        query = 'x=32&y=61;z=135,15&x=16;!(h=134&b=324)'
        arguments = self.request('({})/'.format(query))

        self.assert_arguments(arguments, query=query)

    def test_query_directives(self):
        query = 'x:asc=32&y:desc=61;z:-=135,15&x:descending=16;!(h=134&b=324)'
        arguments = self.request('({})/'.format(query))

        self.assert_arguments(arguments, query=query)

    def test_directive(self):
        arguments = self.request(':random/')

        self.assert_arguments(arguments, directives=['random'])

    def test_directives(self):
        directives = ['random', 'rand', 'other', 'weird', 'wan']
        url = ':{}/'.format(':'.join(directives))
        arguments = self.request(url)

        self.assert_arguments(arguments, directives=directives)

    def test_directives_query(self):
        directives = ['random', 'rand', 'other', 'weird', 'wan']
        url = ':{}(x=4&y=234&z=34)/'.format(':'.join(directives))
        arguments = self.request(url)

        self.assert_arguments(
            arguments, directives=directives, query='x=4&y=234&z=34')

    def test_path(self):
        path = 'this/is/a/path/to/somewhere'
        arguments = self.request('/124/{}/'.format(path))

        self.assert_arguments(arguments, slug='124', path=path)

    def test_query_path(self):
        query = 'x=34&t:desc=324&(x=234&x:asc=2134)'
        path = 'this/is/a(x=324)/path(y=3124&x=23)/to/somewhere'
        arguments = self.request('({})/555/{}/'.format(
            query, path))

        self.assert_arguments(arguments, slug='555', query=query, path=path)

    def test_path_query(self):
        path = 'this/is/a(x=324)/path(y=3124&x=23)/to/somewhere'
        arguments = self.request('/124/{}/'.format(path))

        self.assert_arguments(arguments, slug='124', path=path)

    def test_extension(self):
        ext = 'json'
        arguments = self.request('.{}/'.format(ext))

        self.assert_arguments(arguments, extensions=[ext])

    def test_extensions(self):
        exts = ['schema', 'json']
        arguments = self.request('.{}/'.format('.'.join(exts)))

        self.assert_arguments(arguments, extensions=exts)

    def test_extensions_slug(self):
        exts = ['schema', 'json']
        arguments = self.request('/234.{}/'.format('.'.join(exts)))

        self.assert_arguments(arguments, slug='234', extensions=exts)

    def test_extensions_path(self):
        exts = ['schema', 'json']
        url = '/234/from/this/to/that.{}/'.format('.'.join(exts))
        arguments = self.request(url)

        self.assert_arguments(
            arguments, slug='234', extensions=exts,
            path='from/this/to/that')

    def test_all(self):
        extensions = ['schema', 'json']
        directives = ['random', 'rand', 'okay', 'because']
        slug = '2342fsdg8920sd-235-f-g325-sg23-532'
        path = '/from/this(x=235)/to:random/that(because)/and/this'
        query = 'x=345&xv=32;!(x=34)'
        url = ':{}({})/{}/{}.{}/'.format(
            ':'.join(directives),
            query,
            slug,
            path,
            '.'.join(extensions))
        arguments = self.request(url)

        self.assert_arguments(
            arguments,
            slug=slug,
            extensions=extensions,
            directives=directives,
            path=path,
            query=query)

    def test_extension_path(self):
        url = '/23/from/this.hub/32/from.hub/32/'
        arguments = self.request(url)

        self.assert_arguments(
            arguments,
            slug='23',
            path='from/this.hub/32/from.hub/32')
