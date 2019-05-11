#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

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
