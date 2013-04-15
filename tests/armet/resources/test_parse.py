# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import six
from armet import test
from tests.utils.mock import spy


class ParseTestCase(test.TestCase):

    def request(self, url):
        # Spy on the initialize method.
        target = 'armet.resources.resource.base.Resource'
        with spy(target, '__init__') as method:
            # Invoke a request against the resource.
            response, _ = self.client.request(url)

        # Grab the keyword arguments that were passed into the mocked
        # method.
        arguments = method.call_args[1]

        # Assert that we got enough of them.
        self.assertIn('slug', arguments)
        self.assertIn('query', arguments)
        self.assertIn('extensions', arguments)
        self.assertIn('directives', arguments)
        self.assertIn('path', arguments)

        # Return the arguments
        return arguments

    def assertArguments(self, arguments, **kwargs):
        for argument in kwargs:
            value = arguments.pop(argument)
            self.assertEqual(value, kwargs[argument])

        for name, value in six.iteritems(arguments):
            test = [] if name.endswith('s') else None
            self.assertEqual(value, test)

    def test_simple(self):
        arguments = self.request('/api/simple/')

        self.assertArguments(arguments)

    def test_slug(self):
        arguments = self.request('/api/simple/123/')

        self.assertArguments(arguments, slug='123')

    def test_slug_long(self):
        arguments = self.request('/api/simple/sdf-sdg-sgh-sh234-bf/')

        self.assertArguments(arguments, slug='sdf-sdg-sgh-sh234-bf')

    def test_query(self):
        arguments = self.request('/api/simple(stuff=32)/')

        self.assertArguments(arguments, query='stuff=32')

    def test_query_long(self):
        query = 'x=32&y=61;z=135,15&x=16;!(h=134&b=324)'
        arguments = self.request('/api/simple({})/'.format(query))

        self.assertArguments(arguments, query=query)

    def test_query_directives(self):
        query = 'x:asc=32&y:desc=61;z:-=135,15&x:descending=16;!(h=134&b=324)'
        arguments = self.request('/api/simple({})/'.format(query))

        self.assertArguments(arguments, query=query)

    def test_directive(self):
        arguments = self.request('/api/simple:random/')

        self.assertArguments(arguments, directives=['random'])

    def test_directives(self):
        directives = ['random', 'rand', 'other', 'weird', 'wan']
        url = '/api/simple:{}/'.format(':'.join(directives))
        arguments = self.request(url)

        self.assertArguments(arguments, directives=directives)

    def test_directives_query(self):
        directives = ['random', 'rand', 'other', 'weird', 'wan']
        url = '/api/simple:{}(x=4&y=234&z=34)/'.format(':'.join(directives))
        arguments = self.request(url)

        self.assertArguments(
            arguments, directives=directives, query='x=4&y=234&z=34')

    def test_path(self):
        path = 'this/is/a/path/to/somewhere'
        arguments = self.request('/api/simple/124/{}/'.format(path))

        self.assertArguments(arguments, slug='124', path=path)

    def test_query_path(self):
        query = 'x=34&t:desc=324&(x=234&x:asc=2134)'
        path = 'this/is/a(x=324)/path(y=3124&x=23)/to/somewhere'
        arguments = self.request('/api/simple({})/555/{}/'.format(
            query, path))

        self.assertArguments(arguments, slug='555', query=query, path=path)

    def test_path_query(self):
        path = 'this/is/a(x=324)/path(y=3124&x=23)/to/somewhere'
        arguments = self.request('/api/simple/124/{}/'.format(path))

        self.assertArguments(arguments, slug='124', path=path)

    def test_extension(self):
        ext = 'json'
        arguments = self.request('/api/simple.{}/'.format(ext))

        self.assertArguments(arguments, extensions=[ext])

    def test_extensions(self):
        exts = ['schema', 'json']
        arguments = self.request('/api/simple.{}/'.format('.'.join(exts)))

        self.assertArguments(arguments, extensions=exts)

    def test_extensions_slug(self):
        exts = ['schema', 'json']
        arguments = self.request('/api/simple/234.{}/'.format('.'.join(exts)))

        self.assertArguments(arguments, slug='234', extensions=exts)

    def test_extensions_path(self):
        exts = ['schema', 'json']
        url = '/api/simple/234/from/this/to/that.{}/'.format('.'.join(exts))
        arguments = self.request(url)

        self.assertArguments(
            arguments, slug='234', extensions=exts,
            path='from/this/to/that')

    def test_all(self):
        extensions = ['schema', 'json']
        directives = ['random', 'rand', 'okay', 'because']
        slug = '2342fsdg8920sd-235-f-g325-sg23-532'
        path = '/from/this(x=235)/to:random/that(because)/and/this'
        query = 'x=345&xv=32;!(x=34)'
        url = '/api/simple:{}({})/{}/{}.{}/'.format(
            ':'.join(directives),
            query,
            slug,
            path,
            '.'.join(extensions))
        arguments = self.request(url)

        self.assertArguments(
            arguments,
            slug=slug,
            extensions=extensions,
            directives=directives,
            path=path,
            query=query)

    def test_extension_path(self):
        url = '/api/simple/23/from/this.hub/32/from.hub/32/'
        arguments = self.request(url)

        self.assertArguments(
            arguments,
            slug='23',
            path='from/this.hub/32/from.hub/32'
        )
