#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import logging
import os
import urllib
import webapp2

from epfl.courses import base_handler
from epfl.courses import config
from epfl.courses import models
from epfl.courses import search


class SearchPagination(object):
  
  def __init__(self, results):
    self.offset = results.offset
    self.total_found = results.number_found
    self.total_pages = 0
    self.pages = []
    self.page = None
    self.prev_offset = None
    self.next_offset = None
    
    if self.total_found:
      self.total_pages = (self.total_found-1)/config.PAGE_SIZE + 1
      
      for i in range(self.total_pages):
        self.pages.append((i, i*config.PAGE_SIZE))
      
      self.page = self.offset/config.PAGE_SIZE
      
      if self.page > 0:
        self.prev_offset = (min(self.page, self.total_pages) - 1)*config.PAGE_SIZE
      if self.page < self.total_pages - 1:
        self.next_offset = (self.page + 1)*config.PAGE_SIZE
    

class CatalogPage(base_handler.BaseHandler):

  def BuildQueryFromRequest(self):
    def append_filter(query, id_name, field_name):
      field_value = self.request.get(id_name)
      
      if field_value:
        if " " in field_value:
          field_value = '"%s"' % field_value
        query.ReplaceFilter(field_name, field_value)
      
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
  
  def RecordQuery(self, query_string, offset):
    q_record = models.SearchQueryRecord()
    q_record.q = self.request.get("q")
    q_record.aq_t = self.request.get("aq_t")
    q_record.aq_lang = self.request.get("aq_lang")
    q_record.aq_in = self.request.get("aq_in")
    q_record.aq_sec = self.request.get("aq_sec")
    q_record.aq_sem = self.request.get("aq_sem")
    q_record.aq_exam = self.request.get("aq_exam")
    q_record.aq_cred = self.request.get("aq_cred")
    q_record.aq_coeff = self.request.get("aq_coeff")
    q_record.aq_hours_l = self.request.get("aq_hours_l")
    q_record.aq_hours_r = self.request.get("aq_hours_r")
    q_record.aq_hours_p = self.request.get("aq_hours_p")
    
    q_record.translated_query = query_string
    q_record.offset = offset
    
    q_record.client_address = os.environ["REMOTE_ADDR"]
    
    q_record.put()
    
    return q_record
  
  @webapp2.cached_property
  def section_data(self):
    data = []
    for school in models.School.all():
      sections = []
      for section in school.section_set:
        sections.append((section.code, section.display_name()))

      sections.sort(key=lambda section: section[1])
      data.append((school.code if school.code != models.School.OTHER else "",
                   school.title(), sections))

    data.sort(key=lambda school: school[1])
    
    return data
    
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
                                                   search.SiteSearchProvider()])
        
    autocorr_provider = search.AutocorrectedSearchProvider(
      staged_provider, exact_search=exact_search)
    
    if query_string:
      logging.info("Invoking original search query '%s'" % query_string)
      
      q_record = self.RecordQuery(query_string, offset)
      
      autocorr_provider.Search(query,
                               search_results,
                               limit=config.PAGE_SIZE,
                               offset=offset,
                               accuracy=ACCURACY)
      
      if search_results.results:
        q_record.results_count = search_results.number_found
        q_record.suggested_query = autocorr_provider.suggested_query
        q_record.put()
        
        found_courses = models.Course.get_by_key_name(search_results.results)
        found_courses = filter(lambda course: course is not None, found_courses)
    
    template_args = {
      'courses': found_courses,
      'static': {
        'sections': self.section_data,
        'exam': config.EXAM,
        'credits': config.CREDITS,
        'coeff': config.COEFFICIENT,
        'lecture': config.LECTURE_TIME,
        'recitation': config.RECITATION_TIME,
        'project': config.PROJECT_TIME,
        'samples': config.SAMPLE_QUERIES,
      },
      'query': query_string,
      'original_query': autocorr_provider.original_query,
      'suggested_query': autocorr_provider.suggested_query,
      'offset': search_results.offset,
      'exact': exact_search,
      'pagination': SearchPagination(search_results),
      'debug_mode': (os.environ['SERVER_NAME'].endswith('appspot.com')
                     or os.environ['SERVER_NAME'].endswith('localhost')),
      'debug': {
        'results': search_results.results,
        'provider': None,
        'url': search_results.original_url_,
      },
    }
    
    self.RenderTemplate('catalog.html', template_args)
    

class CoursePage(base_handler.BaseHandler):
  def ComputeSectionHierarchy(self, course):
    course.sections_ = zip(course.sections, course.study_plans, course.urls)
    
    course.hierarchy_ = {}
    
    for section_trio in course.sections_:
      school = section_trio[0].school
      school_title = course.hierarchy_.setdefault("%s - %s" % (school.code,
                                                               school.title()),
                                                  {})
      
      section_ = school_title.setdefault(section_trio[0].title(),
                                         (section_trio[0].code, []))
      section_[1].append((config.STUDY_PLANS[section_trio[1]], section_trio[1]))
    
  def ComputeHoursVisibility(self, course):
    show_vector = [getattr(course, '%s_time' % s, None)
                   and not getattr(course, '%s_weeks' % s, None)
                   for s in ["lecture", "recitation", "project"]]
    
    course.show_trio_ = not reduce(lambda x, y: x or y, show_vector)
    
  def DecodeLinksURLs(self, course):
    decoded_links = [urllib.unquote_plus(link) for link in course.links]
    course.links_ = zip(course.links, decoded_links)
    
  def get(self, course_key, lang=None):
    if not lang:
      return self.redirect_to("course", course_key=course_key, lang="en")
    if lang not in ["en", "fr"]:
      self.abort(404)
    
    course = models.Course.get_by_key_name("%s:%s" % (lang, course_key))
    
    if not course:
      self.abort(404)
    
    self.ComputeSectionHierarchy(course)
    self.ComputeHoursVisibility(course)
    self.DecodeLinksURLs(course)
    
    template_args = {
      "course": course,
      "back_link": self.uri_for("catalog", q=self.request.get("orig_q", ""),
                                offset=self.request.get("orig_offset", ""),
                                exact=self.request.get("orig_exact", "")),
    }
    
    self.RenderTemplate('course.html', template_args)
