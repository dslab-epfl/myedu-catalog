#!/usr/bin/env python

"""The main web application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import webapp2

from webapp2_extras import routes

from epfl.courses import admin
from epfl.courses import base_handler
from epfl.courses import catalog
from epfl.courses import descriptions

config = {}
config['webapp2_extras.sessions'] = {
  'secret_key': 'our secret plan is world domination'
}


class MainPage(base_handler.BaseHandler):
  def get(self):
    self.RenderTemplate("main.html", {})


# TODO(bucur): Hide the administration URLs
# TODO(bucur): Major restructuring of the app
app = webapp2.WSGIApplication([
   webapp2.Route('/', handler=MainPage),
   webapp2.Route('/showcase', handler=catalog.ShowcasePage),
   webapp2.Route('/catalog', handler=catalog.CatalogPage),
   webapp2.Route('/c/<course_key>', handler=catalog.CoursePage,
                 handler_method="get_frontend"),
   webapp2.Route('/update', handler=descriptions.CourseDescriptionPage),
   webapp2.Route('/update/data.xls', handler=descriptions.DumpCSVHandler),
   webapp2.Route('/gcs', handler=catalog.GoogleSearchHandler),
   routes.PathPrefixRoute('/admin', [
     webapp2.Route('/submit', handler=descriptions.SubmitCourseDescription),
     webapp2.Route('/logout', handler=descriptions.LogoutHandler),
     webapp2.Route('/reinit', handler=admin.ReinitDataHandler),
     webapp2.Route('/sections/populate', handler=admin.PopulateSections),
     webapp2.Route('/sections/transition', handler=admin.ConnectSections),
     webapp2.Route('/index', handler=admin.BuildSearchIndexHandler),
     webapp2.Route('/dump', handler=admin.DumpHandler),
     #webapp2.Route('/stats', handler=admin.StatsHandler),
     webapp2.Route('/qstats', handler=admin.QueryStatsHandler),
     webapp2.Route('/sitemap.xml', handler=admin.SitemapHandler),
     webapp2.Route('/sitemap.json', handler=admin.JSONSitemapHandler),
     webapp2.Route('/c/<course_key>.json', handler=catalog.CoursePage,
                   handler_method="get_backend"),
   ])],
   debug=True, config=config)
