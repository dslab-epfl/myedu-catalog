
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import logging
import os
import webapp2

from google.appengine.ext import db

from epfl.courses import models
from epfl.courses import search

jinja_environment = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
  

class CatalogPage(webapp2.RequestHandler):
    
  def get(self):
    PAGE_SIZE = 50
    ACCURACY = 2000
    
    query_string = search.AppEngineSearch.BuildQuery(self.request)
    
    found_courses = None
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
        search_results = search.AppEngineSearch.Search(query_string,
                                                       limit=PAGE_SIZE,
                                                       number_found_accuracy=ACCURACY,
                                                       offset=offset,
                                                       ids_only=True)
        
        found_courses = db.get([document.doc_id
                                for document in search_results.results])
        
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
      'found_courses': found_courses,
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
