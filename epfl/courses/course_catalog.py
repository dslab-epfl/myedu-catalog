
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import os
import webapp2

from epfl.courses import model

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CatalogPage(webapp2.RequestHandler):
  def get(self):
    courses_query = model.Course.all()
    
    courses = courses_query.run()
    
    template = jinja_environment.get_template('catalog.html')
    self.response.out.write(template.render(courses=courses))

class CoursePage(webapp2.RequestHandler):
  def get(self):
    pass

app = webapp2.WSGIApplication([('/', CatalogPage)])
