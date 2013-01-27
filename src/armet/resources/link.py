ALTERNATE           = 'alternate'
APPENDIX            = 'appendix'
ARCHIVES            = 'archives'
AUTHOR              = 'author'
BOOKMARK            = 'bookmark'
CANONICAL           = 'canonical'
CHAPTER             = 'chapter'
COLLECTION          = 'collection'
CONTENTS            = 'contents'
COPYRIGHT           = 'copyright'
CREATE_FORM         = 'create-form'
CURRENT             = 'current'
DESCRIBEDBY         = 'describedby'
DISCLOSURE          = 'disclosure'
DUPLICATE           = 'duplicate'
EDIT                = 'edit'
EDIT_FORM           = 'edit-form'
EDIT_MEDIA          = 'edit-media'
ENCLOSURE           = 'enclosure'
FIRST               = 'first'
GLOSSARY            = 'glossary'
HELP                = 'help'
HOSTS               = 'hosts'
HUB                 = 'hub'
ICON                = 'icon'
INDEX               = 'index'
ITEM                = 'item'
LAST                = 'last'
LATEST_VERSION      = 'latest-version'
LICENSE             = 'license'
LRDD                = 'lrdd'
MONITOR             = 'monitor'
MONITOR_GROUP       = 'monitor-group'
NEXT                = 'next'
NEXT_ARCHIVE        = 'next-archive'
NOFOLLOW            = 'nofollow'
NOREFERRER          = 'noreferrer'
PAYMENT             = 'payment'
PREDECESSOR_VERSION = 'predecessor-version'
PREFETCH            = 'prefetch'
PREV                = 'prev'
PREVIOUS            = 'previous'
PREV_ARCHIVE        = 'prev-archive'
RELATED             = 'related'
REPLIES             = 'replies'
SEARCH              = 'search'
SECTION             = 'section'
SELF                = 'self'
SERVICE             = 'service'
START               = 'start'
STYLESHEET          = 'stylesheet'
SUBSECTION          = 'subsection'
SUCCESSOR_VERSION   = 'successor-version'
TAG                 = 'tag'
UP                  = 'up'
VERSION_HISTORY     = 'version-history'
VIA                 = 'via'
WORKING_COPY        = 'working-copy'
WORKING_COPY_OF     = 'working-copy-of'


class Link:

    def __init__(self, *args, **kwargs):
        print args
        self.uri = kwargs.get('uri')
        self.rel = kwargs.get('rel', RELATED)
        self.title = kwargs.get('title')


    def __str__(self):
        string = "<{}>;rel={}".format(self.uri, self.rel)

        if self.title:
            string += ''.join((';title=', self.title))

        return string
