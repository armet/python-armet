Specification
*************

Notational Conventions
----------------------
This document uses the Augmented Backus-Naur Form (ABNF) notation of
[RFC3986_], and explicitly includes the following rules: pchar.


.. _RFC3986: http://tools.ietf.org/html/rfc3986#appendix-A

Collected ABNF
--------------

::

    query = query-expression *( query-separator query-expression )

    query-separator = ";" / "&"

    query-expression = query-expression-simple
                     / [query-expression-simple-negation] "(" query ")"

    query-expression-simple-negation = "not" / "!"

    query-expression-simple = query-expression-name
                              [query-expression-operation]
                              [query-expression-negation]
                              ["=" query-expression-value]

    query-expression-name = *pchar *( "." *pchar ) [ "@" *pchar ]
                          / "@" *pchar

    query-expression-negation = ( query-expression-separator "not" )
                              / "!"

    query-expression-operation = "." query-expression-operation-name

    query-expression-operation-name = "exact"
                                    / "iexact"
                                    / "contains"
                                    / "icontains"
                                    / "regex"
                                    / "iregex"
                                    / "gt"
                                    / "gte"
                                    / "lt"
                                    / "lte"
                                    / "startswith"
                                    / "istartswith"
                                    / "endswith"
                                    / "iendswith"
                                    / "isnull"

    query-expression-value = *pchar *( "," *pchar )
