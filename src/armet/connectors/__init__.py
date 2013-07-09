# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six


#! List of available HTTP/1.1 connectors.
http = ('bottle', 'flask', 'django',)

# if not six.PY3:
#     # Add python 2.x only connectors.
#     http = ('cyclone',)

#! List of available ORM connectors.
model = ('django', 'sqlalchemy')
