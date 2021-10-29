#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Don't bother with caching, site is too small
LOAD_CONTENT_CACHE = False

AUTHOR = 'Hazel Victoria Campbell'
SITENAME = "Hazel's Zone"
SITEURL = ''

PATH = 'content'

TIMEZONE = 'America/Edmonton'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ATOM = 'feeds/atom.xml'
FEED_ALL_ATOM = None # This seems redundant
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
FEED_RSS = 'feeds/rss.xml'

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

GITHUB_URL = 'https://github.com/hazelybell'

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# I don't see why I wouldn't just use relative URLS anwyway
RELATIVE_URLS = True

MENUITEMS = (
    ('Contact', 'mailto:me@hazel.zone'),
    ('Github', 'https://github.com/hazelybell'),
    )

# By Stefaan Lippens 2016 https://www.stefaanlippens.net/quick-and-easy-tag-cloud-in-pelican.html
import math
JINJA_FILTERS = {
    'count_to_font_size': lambda c: '{p:.1f}%'.format(p=100 + 25 * math.log(c, 2)),
}

import pygments.lexers
import sys
import os

CUSTOM_HILITERS = os.path.abspath('custom_hiliters.py')
sys.path.insert(0, os.path.dirname(CUSTOM_HILITERS))
import custom_hiliters
for lexer_name in custom_hiliters.__all__:
    lexer = getattr(custom_hiliters, lexer_name)
    module_name = 'custom_hiliters'
    pygments.lexers.LEXERS[lexer_name] = (
        (
            module_name,
            lexer.name,
            tuple(lexer.aliases),
            tuple(lexer.filenames),
            tuple(lexer.mimetypes)
            )
        )

#pygments.lexers.load_lexer_from_file(CUSTOM_HILITERS, lexername='NFTablesLexer')
#pygments.lexers.LEXERS.append()
#pygments.lexers.get_lexer_by_name('nftables')

from pelican.settings import DEFAULT_CONFIG
from copy import deepcopy

MARKDOWN = deepcopy(DEFAULT_CONFIG['MARKDOWN'])

CODEHILITE = MARKDOWN.get('extension_configs', dict()).get('markdown.extensions.codehilite', dict())
CODEHILITE['css_class'] = 'highlight'
CODEHILITE['linenos'] = False
CODEHILITE['lineanchors'] = 'codeline'
CODEHILITE['linespans'] = 'codelinespan'

#try:
    #MARKDOWN
#except NameError:
    #import sys
    #sys.exit(100)
    #MARKDOWN = {
        #'extension_configs': {
            #'markdown.extensions.codehilite': {'css_class': 'highlight'},
            #'markdown.extensions.extra': {},
            #'markdown.extensions.meta': {},
        #},
        #'output_format': 'html5',
    #}
