# -*- coding: utf-8 -*-
"""Defines the link relations and a link factory.
"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from six.moves import cStringIO


class rel:
    """Enumeration of the many link relations found in the IANA registry.

    Relations that are commented out are those that wouldn't make sense
    in the context of a RESTful interface.

    @par Reference
        http://www.iana.org/assignments/link-relations/link-relations.xml
    """

    #! Refers to a substitute for this context.
    ALTERNATE = 'alternate'

    #! Refers to an appendix.
    # APPENDIX = 'appendix'

    #! Refers to a collection of records, documents, or other materials of
    #! historical interest.
    ARCHIVES = 'archives'

    #! Refers to the context's author.
    # AUTHOR = 'author'

    #! Gives a permanent link to use for bookmarking purposes.
    # BOOKMARK = 'bookmark'

    #! Designates the preferred version of a resource (the IRI and
    #! its contents).
    CANONICAL = 'canonical'

    #! Refers to a chapter in a collection of resources.
    # CHAPTER = 'chapter'

    #! The target IRI points to a resource which represents the collection
    #! resource for the context IRI.
    COLLECTION = 'collection'

    #! Refers to a table of contents.
    # CONTENTS = 'contents'

    #! Refers to a copyright statement that applies to the link's context.
    # COPYRIGHT = 'copyright'

    #! The target IRI points to a resource where a submission form can
    #! be obtained.
    # CREATE_FORM = 'create-form'

    #! Refers to a resource containing the most recent item(s) in a
    #! collection of resources.
    CURRENT = 'current'

    #! Refers to a resource providing information about the link's context.
    DESCRIBED_BY = 'describedby'

    #! Refers to a list of patent disclosures made with respect to material
    #! for which 'disclosure' relation is specified.
    DISCLOSURE = 'disclosure'

    #! TODO: Finish this...

    DUPLICATE = 'duplicate'
    EDIT = 'edit'
    EDIT_FORM = 'edit-form'
    EDIT_MEDIA = 'edit-media'
    ENCLOSURE = 'enclosure'
    FIRST = 'first'
    GLOSSARY = 'glossary'
    HELP = 'help'
    HOSTS = 'hosts'
    HUB = 'hub'
    ICON = 'icon'
    INDEX = 'index'
    ITEM = 'item'
    LAST = 'last'
    LATEST_VERSION = 'latest-version'
    LICENSE = 'license'
    LRDD = 'lrdd'
    MONITOR = 'monitor'
    MONITOR_GROUP = 'monitor-group'
    NEXT = 'next'
    NEXT_ARCHIVE = 'next-archive'
    NOFOLLOW = 'nofollow'
    NOREFERRER = 'noreferrer'
    PAYMENT = 'payment'
    PREDECESSOR_VERSION = 'predecessor-version'
    PREFETCH = 'prefetch'
    PREV = 'prev'
    PREVIOUS = 'previous'
    PREV_ARCHIVE = 'prev-archive'
    RELATED = 'related'
    REPLIES = 'replies'
    SEARCH = 'search'
    SECTION = 'section'
    SELF = 'self'
    SERVICE = 'service'
    START = 'start'
    STYLESHEET = 'stylesheet'
    SUBSECTION = 'subsection'
    SUCCESSOR_VERSION = 'successor-version'
    TAG = 'tag'
    UP = 'up'
    VERSION_HISTORY = 'version-history'
    VIA = 'via'
    WORKING_COPY = 'working-copy'
    WORKING_COPY_OF = 'working-copy-of'


class Link:

    def __init__(self, uri, rel=rel.RELATED, title=None):
        """Initializes and stores the link information.

        @param[in] uri
            Absolute (or relative in relation to the link container) URI to the
            resource.

        @param[in] rel
            Kind of relation; defaults to 'related'.
            Should be one of the values enumerated at:
            http://www.iana.org/assignments/link-relations/link-relations.xml
        """
        self.uri = uri
        self.rel = rel
        self.title = title

    def __str__(self):
        """Serialize the link as an HTTP link header."""
        stream = cStringIO()
        stream.write("<{}>;rel={}".format(self.uri, self.rel))
        if self.title is not None:
            stream.write(';title={}'.format(self.title))
        return stream.getvalue()
