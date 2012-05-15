#!/usr/bin/env python

"""The main web application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import os
import webapp2

from webapp2_extras import routes

from epfl.courses import admin
from epfl.courses import course_catalog as ccat
from epfl.courses import course_descriptions as cdesc

config = {}
config['webapp2_extras.sessions'] = {
  'secret_key': 'our secret plan is world domination'
}


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('main.html')
    self.response.out.write(template.render())


app = webapp2.WSGIApplication([
   webapp2.Route('/', handler=MainPage),
   webapp2.Route('/showcase', handler=ccat.ShowcasePage),
   webapp2.Route('/catalog', handler=ccat.CatalogPage),
   webapp2.Route('/c/<course_key>', handler=ccat.CoursePage),
   webapp2.Route('/update', handler=cdesc.CourseDescriptionPage),
   routes.PathPrefixRoute('/admin', [
     webapp2.Route('/search', handler=admin.BuildSearchIndex),
     webapp2.Route('/submit', handler=cdesc.SubmitCourseDescription),
     webapp2.Route('/logout', handler=cdesc.LogoutHandler),
     webapp2.Route('/rebuild', handler=admin.ReinitDataHandler),
     webapp2.Route('/stats', handler=admin.StatsHandler),
     webapp2.Route('/dump', handler=admin.DumpHandler)
   ])],
   debug=True, config=config)
