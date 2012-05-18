
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
    def append_field(query, id_name, field_name):
      field = self.request.get(id_name)
      if field:
        query.append('%s:"%s"' % (field_name, field))

    qdict = {
      "q": self.request.get("q"),
      "title": self.request.get("aq_title"),
      "instructor": self.request.get("aq_instructor"),
      "section": self.request.get("aq_section"),
      "has_words": self.request.get("aq_has_words"),
      "doesnt_have_words": self.request.get("aq_doesnt_have_words")
    }
    
    query = [self.request.get("q", "")]
    append_field(query, "aq_title", "title")
    append_field(query, "aq_instructor", "instructor")
    append_field(query, "aq_section", "section")
    
    if self.request.get("aq_credits"):
      if self.request.get("use_credits") == "coeff":
        append_field(query, "aq_credits", "coefficient")
      else:
        append_field(query, "aq_credits", "credits")
    
    has_words = self.request.get("aq_has_words")
    if has_words:
      query.append('"%s"' % has_words)
      
    doesnt_have_words = self.request.get("aq_doesnt_have_words")
    if doesnt_have_words:
      query.append('(NOT %s' % doesnt_have_words)
    
    return " ".join(query).strip()
    
  def get(self):
    PAGE_SIZE = 50
    ACCURACY = 2000
    
    query_string = self._ParseSearchQuery()
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
    
    show_vector = [getattr(course, '%s_time' % s, None)
                   and not getattr(course, '%s_weeks' % s, None)
                   for s in ["lecture", "recitation", "project", "practical"]]
    
    course.show_trio_ = not reduce(lambda x, y: x or y, show_vector)
    
    template = jinja_environment.get_template('course.html')
    self.response.out.write(template.render(course=course))
    
    
################################################################################
    
    
class ShowcasePage(webapp2.RequestHandler):
  def get(self):
    courses = models.Course.all().order('name').run()
                                     
    template = jinja_environment.get_template('showcase.html')
    self.response.out.write(template.render(courses=courses))
