
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import os
import webapp2

from google.appengine.ext import db


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

language_mapping = {
  "en": "English",
  "fr": "French"
}


class Course(db.Model):
  name = db.StringProperty(required=True)
  language = db.StringProperty(required=True, choices=set(["en", "fr"]))
  teachers = db.StringListProperty()
  studies = db.StringListProperty()
  orientations = db.StringListProperty()
  urls = db.StringListProperty()


class CatalogPage(webapp2.RequestHandler):
  def get(self):
    courses_query = Course.all()
    courses = courses_query.run()
    
    template = jinja_environment.get_template('catalog.html')
    self.response.out.write(template.render(courses=courses))


class CoursePage(webapp2.RequestHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course._language = language_mapping[course.language]
    
    template = jinja_environment.get_template('course.html')
    self.response.out.write(template.render(course=course))


app = webapp2.WSGIApplication([
    (r'/', CatalogPage),
    (r'/c/([0-9a-zA-z\-]+)', CoursePage)], debug=True)
