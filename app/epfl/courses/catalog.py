#!/usr/bin/env python

"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging

from google.appengine.ext import db

from epfl.courses import base_handler
from epfl.courses import models
from epfl.courses import search


class CatalogPage(base_handler.BaseHandler):
    
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
      logging.info("Invoking search query '%s'" % query_string)
      search_results = search.AppEngineSearch.Search(query_string,
                                                     limit=PAGE_SIZE,
                                                     number_found_accuracy=ACCURACY,
                                                     offset=offset,
                                                     ids_only=True)
      
      if search_results:
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
    
    template_args = {
      'courses': found_courses,
      'total_found': total_found,
      'query': query_string,
      'offset': offset,
      'next_offset': next_offset,
      'prev_offset': prev_offset,
      'page': page,
      'total_pages': total_pages,
      'pages': pages
    }
    self.RenderTemplate('catalog.html', template_args)
    

class CoursePage(base_handler.BaseHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course.language_ = models.LANGUAGE_MAPPING[course.language]
    course.sections_ = zip(course.sections, course.urls)
    
    show_vector = [getattr(course, '%s_time' % s, None)
                   and not getattr(course, '%s_weeks' % s, None)
                   for s in ["lecture", "recitation", "project", "practical"]]
    
    course.show_trio_ = not reduce(lambda x, y: x or y, show_vector)
    
    self.RenderTemplate('course.html', { "course": course})
    
class GoogleSearchHandler(base_handler.BaseHandler):
  def get(self):
    self.RenderTemplate('google_search.html', {})

    
################################################################################
    
    
class ShowcasePage(base_handler.BaseHandler):
  def get(self):
    courses = models.Course.all().order('name').run()
    self.RenderTemplate('showcase.html', { "courses": courses})

