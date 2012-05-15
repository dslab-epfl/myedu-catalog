
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import logging
import os
import webapp2

from google.appengine.api import search
from google.appengine.ext import db

from epfl.courses import models

jinja_environment = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
  

class CatalogPage(webapp2.RequestHandler):
  def _ParseSearchQuery(self):
    qdict = {
      "q": self.request.get("q"),
      "title": self.request.get("aq_title"),
      "instructor": self.request.get("aq_instructor"),
      "section": self.request.get("aq_section"),
      "has_words": self.request.get("aq_has_words"),
      "doesnt_have_words": self.request.get("aq_doesnt_have_words")
    }
    
    query = "%s %s %s %s %s %s" % (
      qdict["q"],
      ('title:"%s"' % qdict["title"]) if qdict["title"] else "",
      ('instructor:"%s"' % qdict["instructor"]) if qdict["instructor"] else "",
      ('section:"%s"' % qdict["section"]) if qdict["section"] else "",
      ('"%s"' % qdict["has_words"]) if qdict["has_words"] else "",
      ('(NOT %s)' % qdict["doesnt_have_words"]) if qdict["doesnt_have_words"] else "" 
    )
    
    return query.strip(), qdict
    
  def get(self):
    RESULT_LIST_LIMIT = 50
    
    query_string, qdict = self._ParseSearchQuery()
    courses = None
    total_found = None
    
    try:
      logging.info("Invoking search query '%s'" % query_string)
      query = search.Query(query_string,
                           search.QueryOptions(limit=RESULT_LIST_LIMIT))
      search_results = search.Index(name=models.INDEX_NAME).search(query)
      
      courses = db.get([document.doc_id for document in search_results.results])
      total_found = search_results.number_found
    except:
      logging.exception("Could not perform query")
    
    template_args = {
      'courses': courses,
      'total_found': total_found,
      'query': query_string,
      'qdict': qdict
    }
    template = jinja_environment.get_template('catalog.html')
    self.response.out.write(template.render(template_args))
    

class CoursePage(webapp2.RequestHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course._language = models.LANGUAGE_MAPPING[course.language]
    course._sections = zip(course.sections, course.urls)
    
    template = jinja_environment.get_template('course.html')
    self.response.out.write(template.render(course=course))
    
    
################################################################################
    
    
class ShowcasePage(webapp2.RequestHandler):
  def get(self):
    courses = models.Course.all().order('name').run()
                                     
    template = jinja_environment.get_template('showcase.html')
    self.response.out.write(template.render(courses=courses))
