#!/usr/bin/env python

"""The main web application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import os
import webapp2

import course_catalog as ccat
import course_descriptions as cdesc

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
   webapp2.Route('/', handler=MainPage, name='main'),
   webapp2.Route('/showcase', handler=ccat.ShowcasePage, name='showcase'),
   webapp2.Route('/catalog', handler=ccat.CatalogPage, name='catalog'),
   webapp2.Route('/c/<course_key>', handler=ccat.CoursePage, name='course'),
   webapp2.Route('/ajax/courses', handler=ccat.AjaxCourses, name='ajax_course'),
   webapp2.Route('/admin/search', handler=ccat.BuildSearchIndex, name='search_index'),
   webapp2.Route('/admin/submit', handler=cdesc.SubmitCourseDescription, name='submit_course'),
   webapp2.Route('/admin/logout', handler=cdesc.LogoutHandler, name='logout'),
   webapp2.Route('/update', handler=cdesc.CourseDescriptionPage, name='csp')],
   debug=True, config=config)
