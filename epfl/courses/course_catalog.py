
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
    PAGE_SIZE = 50
    ACCURACY = 2000
    
    query_string, _ = self._ParseSearchQuery()
    courses = None
    total_found = models.Course.TotalCount()
    
    offset = 0
    next_offset = None
    prev_offset = None
    page = None
    total_pages = None
    pages = []
    
    if self.request.get("offset"):
      try:
        offset = int(self.request.get("offset"))
        if offset < 0:
          offset = 0
      except ValueError:
        pass
    
    if query_string:
      try:
        logging.info("Invoking search query '%s'" % query_string)
        query = search.Query(query_string,
                             search.QueryOptions(limit=PAGE_SIZE,
                                                 number_found_accuracy=ACCURACY,
                                                 offset=offset,
                                                 ids_only=True))
        search_results = search.Index(name=models.INDEX_NAME).search(query)
        
        courses = db.get([document.doc_id for document in search_results.results])
        
        if search_results.number_found < total_found:
          total_found = search_results.number_found
        
        if total_found:
          total_pages = (total_found-1)/PAGE_SIZE + 1
          for i in range(total_pages):
            pages.append((i, i*PAGE_SIZE))
          
          page = offset/PAGE_SIZE
          
          if page > 0:
            prev_offset = (min(page, total_pages) - 1)*PAGE_SIZE
          if page < total_pages - 1:
            next_offset = (page + 1)*PAGE_SIZE
        
      except:
        logging.exception("Could not perform query")
    
    template_args = {
      'courses': courses,
      'total_found': total_found,
      'query': query_string,
      'offset': offset,
      'next_offset': next_offset,
      'prev_offset': prev_offset,
      'page': page,
      'total_pages': total_pages,
      'pages': pages
    }
    template = jinja_environment.get_template('catalog.html')
    self.response.out.write(template.render(template_args))
    

class CoursePage(webapp2.RequestHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course.language_ = models.LANGUAGE_MAPPING[course.language]
    course.sections_ = zip(course.sections, course.urls)
    
    template = jinja_environment.get_template('course.html')
    self.response.out.write(template.render(course=course))
    
    
################################################################################
    
    
class ShowcasePage(webapp2.RequestHandler):
  def get(self):
    courses = models.Course.all().order('name').run()
                                     
    template = jinja_environment.get_template('showcase.html')
    self.response.out.write(template.render(courses=courses))
