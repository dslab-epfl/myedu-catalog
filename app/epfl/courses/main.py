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
  }
}


class MainPage(base_handler.BaseHandler):
  def get(self):
    self.RenderTemplate("main.html", {})


app = webapp2.WSGIApplication([
   webapp2.Route('/', handler=MainPage),
   webapp2.Route('/catalog', handler=catalog.CatalogPage),
   webapp2.Route('/course/<course_key>', handler=catalog.CoursePage,
                 name="course"),
   routes.PathPrefixRoute('/admin', [
     webapp2.Route('/reinit', handler=admin.ImportCourseCatalog),
     #webapp2.Route('/sections/populate', handler=admin.PopulateSections),
     #webapp2.Route('/sections/transition', handler=admin.ConnectSections),
     #webapp2.Route('/index', handler=admin.BuildSearchIndexHandler),
     #webapp2.Route('/dump', handler=admin.DumpHandler),
     #webapp2.Route('/stats', handler=admin.StatsHandler),
     #webapp2.Route('/qstats', handler=admin.QueryStatsHandler),
     #webapp2.Route('/sitemap.xml', handler=admin.SitemapHandler),
     #webapp2.Route('/sitemap.json', handler=admin.JSONSitemapHandler),
   ])],
   debug=True, config=config)
