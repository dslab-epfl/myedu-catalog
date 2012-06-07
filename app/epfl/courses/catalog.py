#!/usr/bin/env python

"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import random

from google.appengine.ext import db

from epfl.courses import base_handler
from epfl.courses import models
from epfl.courses import search


class CatalogPage(base_handler.BaseHandler):
    
  def get(self):
    PAGE_SIZE = 20
    ACCURACY = 2000
    
    query = search.parser.SearchQuery.BuildFromRequest(self.request)
    
    if query.directives.get("loc") == "index":
      provider = search.AppSearchProvider
    else:
      provider = search.AppSearchProvider
    
    query_string = query.GetString()
    suggested_string = None
    
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
    
    logging.info("Invoking search query '%s'" % query_string)
    search_results = provider.Search(query,
                                     limit=PAGE_SIZE,
                                     offset=offset,
                                     accuracy=ACCURACY)
    
    if search_results:
      if search_results.original:
        suggested_string = search_results.query
      
      found_courses = db.get(search_results.results)
      
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
      'suggested_query': suggested_string,
      'offset': offset,
      'next_offset': next_offset,
      'prev_offset': prev_offset,
      'page': page,
      'total_pages': total_pages,
      'pages': pages
    }
    self.RenderTemplate('catalog.html', template_args)
    

class CoursePage(base_handler.BaseHandler):
  def AnnotateCourseEntry(self, course):
    course.language_ = models.LANGUAGE_MAPPING[course.language]
    course.sections_ = zip(course.sections, course.urls)
    
    show_vector = [getattr(course, '%s_time' % s, None)
                   and not getattr(course, '%s_weeks' % s, None)
                   for s in ["lecture", "recitation", "project", "practical"]]
    
    course.show_trio_ = not reduce(lambda x, y: x or y, show_vector)
    
  def get_frontend(self, course_key):
    course = db.get(course_key)
    self.AnnotateCourseEntry(course)
    
    template_args = {
      "course": course
    }
    
    self.RenderTemplate('course.html', template_args)
    
  def get_backend(self, course_key):
    course = db.get(course_key)
    self.AnnotateCourseEntry(course)
    
    template_args = {
      "course": course,
      "no_title": True
    }
    
    course_page = self.GetRenderedTemplate('course_body.html', template_args)
    
    data = {
      "id": course_key,
      "title": course.title,
      "html": course_page
    }
    
    self.RenderJSON(data)


class GoogleSearchHandler(base_handler.BaseHandler):
  def get(self):
    self.RenderTemplate('google_search.html', {})

    
################################################################################
    
    
class ShowcasePage(base_handler.BaseHandler):
  def get(self):
    SECTIONS = {
      'AR': "Architecture",
      'EL': "Electrical Engineering",
      'IN': "Computer Science",
      'MA': "Mathematics",
      'SV': "Life Sciences"
    }
    
    COLORS = [
      "f5ffff",
      "fffdeb",
      "fefcff",
      "ffeffc",
      "eefff5"
    ]
    
    sections = []
    for section in sorted(SECTIONS.keys()):
      course_set = models.Course.all().filter("sections", section).order('title').fetch(None)
      logging.info("Found %d courses in section %s" % (len(course_set), section))
      for course in course_set:
        course.color_ = random.choice(COLORS)
        
      sections.append ({
        "id": section,
        "name": SECTIONS[section],
        "courses": course_set
      })
    
    self.RenderTemplate('showcase.html', { "sections": sections})

