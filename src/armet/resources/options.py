# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
import re


class ResourceOptions(object):

    def __init__(self, options, name):
        """
        Initializes the options object and defaults configuration not
        specified.

        @param[in] options
            Dictionary of the merged options attributes.

        @param[in] name
            Name of the resource class this is being instantiataed for.
        """
        #! Name of the resource to use in URIs; defaults to the dasherized
        #! version of the camel cased class name (eg. SomethingHere becomes
        #! something-here). The defaulted version also strips a trailing
        #! Resource from the name (eg. SomethingHereResource still becomes
        #! something-here).
        self.name = options.get('name')
        if self.name is None:
          # Generate a name for the resource if one is not provided.
          # PascalCaseThis => pascal-case-this
          names = re.findall(r'[A-Z]?[a-z]+|[0-9]+/g', name)
          if len(names) > 1 and names[-1].lower() == 'resource':
              # Strip off a trailing Resource as well.
              names = names[:-1]
          self.name = '-'.join(names).lower()
