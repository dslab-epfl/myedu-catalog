#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""The main web application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import webapp2

from webapp2_extras import routes

from epfl.courses import admin
from epfl.courses import base_handler
from epfl.courses import catalog

config = {}
config['webapp2_extras.sessions'] = {
  'secret_key': 'our secret plan is world domination'
}

config['webapp2_extras.jinja2'] = {
  'filters': {
    'isamarkup': base_handler.BaseHandler.ISAMarkup,
  },
  'globals': {
    'url_for': webapp2.uri_for,
  }
}


app = webapp2.WSGIApplication([
   webapp2.Route('/sitemap.xml', handler=admin.SitemapHandler),
   
   webapp2.Route('/', handler=catalog.LanguageRedirect,
                 name="catalog-redir"),
   routes.RedirectRoute('/course/<course_key>',
                        handler=catalog.LanguageRedirect, name="course-redir"),
   
   routes.PathPrefixRoute('/<lang:\w+>', [
     routes.RedirectRoute('/', handler=catalog.CatalogPage,
                          name="catalog", strict_slash=True),
                               
     routes.RedirectRoute('/course', name="no-course",
                          redirect_to_name="catalog", strict_slash=True),
     routes.RedirectRoute('/course/<course_key>', handler=catalog.CoursePage,
                           name="course", strict_slash=True),
   ]),
                               
   routes.PathPrefixRoute('/admin', [
     webapp2.Route('/reinit/<operation>', handler=admin.ImportCourseCatalog),
     webapp2.Route('/index/<operation>', handler=admin.BuildSearchIndexHandler),
     webapp2.Route('/qstats', handler=admin.QueryStatsHandler),
     webapp2.Route('/section/<sec_id>/remove/<dest_id>',
                   handler=admin.RemoveSectionHandler),
   ])],
   debug=True, config=config)
