#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import random
import os

from google.appengine.ext import db

from epfl.courses import base_handler
from epfl.courses import models
from epfl.courses import search

class SearchPagination(object):
  PAGE_SIZE = 20
  
  def __init__(self, results):
    self.offset = results.offset
    self.total_found = results.number_found
    self.total_pages = 0
    self.pages = []
    self.page = None
    self.prev_offset = None
    self.next_offset = None
    
    if self.total_found:
      self.total_pages = (self.total_found-1)/self.PAGE_SIZE + 1
      
      for i in range(self.total_pages):
        self.pages.append((i, i*self.PAGE_SIZE))
      
      self.page = self.offset/self.PAGE_SIZE
      
      if self.page > 0:
        self.prev_offset = (min(self.page, self.total_pages) - 1)*self.PAGE_SIZE
      if self.page < self.total_pages - 1:
        self.next_offset = (self.page + 1)*self.PAGE_SIZE
    

class CatalogPage(base_handler.BaseHandler):

  def BuildQueryFromRequest(self):
    def append_filter(query, id_name, field_name):
      field_value = self.request.get(id_name)
      if field_value:
        query.filters.append((field_name, field_value))
      
    query = search.SearchQuery.ParseFromString(self.request.get("q", ""))
    
    append_filter(query, "aq_t", "title")
    append_filter(query, "aq_lang", "language")
    append_filter(query, "aq_in", "instructor")
    append_filter(query, "aq_sec", "section")
    append_filter(query, "aq_sem", "semester")
    append_filter(query, "aq_exam", "exam")
    append_filter(query, "aq_cred", "credits")
    append_filter(query, "aq_coeff", "coefficient")
    
    append_filter(query, "aq_hours_l", "lecthours")
    append_filter(query, "aq_hours_r", "recithours")
    append_filter(query, "aq_hours_p", "projhours")
    
    return query
  
  def GetOffsetFromRequest(self):
    offset = 0
    
    if self.request.get("offset"):
      try:
        offset = int(self.request.get("offset"))
        if offset < 0:
          offset = 0
      except ValueError:
        pass
      
    return offset
    
  def get(self):
    ACCURACY = 2000
    
    query = self.BuildQueryFromRequest()
    offset = self.GetOffsetFromRequest()
    
    query_string = query.GetString()
    found_courses = None
    search_results = search.SearchResults(query_string, offset)
    exact_search = self.request.get("exact")
    
    # Create the composite search engine
    staged_provider = search.StagedSearchProvider([search.AppSearchProvider,
                                                   search.SiteSearchProvider])
        
    autocorr_provider = search.AutocorrectedSearchProvider(
      staged_provider, exact_search=exact_search)
    

    
    if query_string:
      logging.info("Invoking original search query '%s'" % query_string)
      
      autocorr_provider.Search(query,
                               search_results,
                               limit=SearchPagination.PAGE_SIZE,
                               offset=offset,
                               accuracy=ACCURACY)
      
      if search_results.results and search_results.offset == offset:
        if os.environ['SERVER_SOFTWARE'].startswith('Development'):
          found_courses = []
        else:
          found_courses = db.get(search_results.results)
    
    template_args = {
      'courses': found_courses,
      'query': query_string,
      'original_query': autocorr_provider.original_query,
      'suggested_query': autocorr_provider.suggested_query,
      'offset': search_results.offset,
      'exact': exact_search,
      'pagination': SearchPagination(search_results),
      'debug': {
        'results': search_results.results,
        'provider': None,
        'url': search_results.original_url_,
      },
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

