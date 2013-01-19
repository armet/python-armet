

RELATED = 'related'

class Link:

    def __init__(self, **kwargs):
        self.uri = kwargs.get('uri')
        self.rel = kwargs.get('rel', RELATED)
        self.title = kwargs.get('title')


    def __str__(self):
        string = "<{}>;rel={}".format(self.uri, self.title)

        if self.title:
            string += ''.join(('title=', self.title))

        return string

        # if self.uri and self.title
        #     return '<'+self.uri+'>;rel='+RELATED+';title='+self.title

        # if self.uri and not self.title
        #     return '<'+self.uri+'>;rel='+RELATED




"""
# Expected usage:
from armet.resources import link
x = link.Link(uri="question", rel=link.RELATED, title="question")
str(x) # == <question>;rel=related;title=question


x = link.Link(uri="question", rel=link.RELATED)
str(x) # == <question>;rel=related
"""
