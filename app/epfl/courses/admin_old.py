#!/usr/bin/env python

"""Administration tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import datetime
import logging
import pprint

from google.appengine.ext import db
from google.appengine import runtime

from epfl.courses import base_handler
from epfl.courses import imports
from epfl.courses import models
from epfl.courses import static_data
from epfl.courses.search import appsearch_admin as appsearch
from epfl.courses.search import parser


class DumpHandler(base_handler.BaseHandler):
  """Shamelessly dumps the entire course information."""
  def DumpTitles(self):
    results = models.Course.all().run(projection=('title', 'urls'))
    
    data = [{ "id": str(course.key()), "title": course.title, "urls": course.urls[0]}
            for course in results]
    
    return data
  
  def DumpAll(self):
    data = []
    for course in models.Course.all().run():
      props = {}
      
      props["meta"] = {
        "key_id": str(course.key()),
        "id": str(course.key().id()),
      }
      
      for prop in models.Course.properties():
        props[prop] = getattr(course, prop)
        
      data.append(props)
    
    return data
  
  def get(self):
    if self.request.get("all"):
      data = self.DumpAll()
    else:
      data = self.DumpTitles()
    
    self.SetAttachment("dump.json")
    self.RenderJSON(data)


class ReinitDataHandler(base_handler.BaseHandler):
    
  def DeleteAllCourses(self):
    logging.info("Deleting all course information")
    course_keys = models.Course.all(keys_only=True).fetch(None)
    db.delete(course_keys)
    logging.info("Deleted %d courses.\n" % len(course_keys))
    
  def get(self):
    course_list = None
    if self.request.get("rebuild"):
      self.DeleteAllCourses()
      course_list = imports.RebuildFromCSV()
      logging.info("Added %d courses.\n" % len(course_list))    

    imports.UpdateCoursesFromCrawl(course_list)
    
    self.SetTextMode()
    self.response.out.write('OK.\n')
    
    
class BuildSearchIndexHandler(base_handler.BaseHandler):
  def get(self):
    self.SetTextMode()
    
    if self.request.get("erase"):
      appsearch.AppEngineIndex.ClearCourseIndex()
      self.response.out.write('OK.\n')
      return
    
    if self.request.get("rebuild"):
      courses = models.Course.all().fetch(None)
      appsearch.AppEngineIndex.ClearIndexingStatus(courses)
    
    if appsearch.AppEngineIndex.UpdateCourseIndex():
      self.response.out.write('OK.\n')
    else:
      self.response.out.write("Search quota exceeded. Try again later.\n")
      
      
class PopulateSections(base_handler.BaseHandler):
  def get(self):
    for school in static_data.SCHOOLS.values():
      models.School(key_name=school.code,
                    title_en=school.title_en,
                    title_fr=school.title_fr).put()
                    
    for section in static_data.SECTIONS.values():
      models.Section(key_name=section.code,
                     title_short=section.title_short,
                     title_en=section.title_en,
                     title_fr=section.title_fr,
                     school=models.School.get_by_key_name(section.school),
                     minor=section.minor,
                     doctoral=section.doctoral,
                     meta=section.meta).put()
                     
    for study_plan in static_data.STUDY_PLANS.values():
      models.StudyPlan(key_name=study_plan.code,
                       section=models.Section.get_by_key_name(study_plan.section.code),
                       plan=study_plan.plan_code,
                       semester=study_plan.semester_code).put()
                       
    self.SetTextMode()
    self.response.out.write('OK.\n')
    
    
class ConnectSections(base_handler.BaseHandler):
  def get(self):
    self.SetTextMode()
    
    skipped = 0
    processed = 0
    
    try:
      for course in models.Course.all():
        if course.section_keys and course.study_plan_keys:
          skipped += 1
          continue
        
        course.section_keys = [models.Section.get_by_key_name(section).key()
                               for section in course.sections]
        course.study_plan_keys = [models.StudyPlan.get_by_key_name(study_plan).key()
                                  for study_plan in course.study_plans]
        course.put()
        processed += 1
    except runtime.DeadlineExceededError:
      self.response.out.write("Could not process all. Skipped: %d. Processed: %d.\n" % (skipped, processed))
    else:
      self.response.out.write('OK.\n')


class StatsHandler(base_handler.BaseHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    
    sections = {}
    studies = {}
    
    for course in models.Course.all().run():
      for section in course.sections:
        sections[section] = sections.get(section, 0) + 1
      for study in course.study_plans:
        studies[study] = studies.get(study, 0) + 1
        
    pprint.pprint(sections, self.response.out)
    pprint.pprint(studies, self.response.out)


class QueryStatsHandler(base_handler.BaseHandler):
  LAUNCH_DATE = datetime.datetime(2012, 6, 14, 17, 20)
  
  CANNED_QUERIES = [
    'plan:"SHS-BA3" literature OR design',
    'credits:2 "organic materials"',
    'semester:fall java',
    'section:"MIN_IN_SEC" -cryptography'
  ]
  
  PAGE_SIZE = 20
  
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    
    count = 0
    canned_count = 0
    
    no_results = []
    many_results = []
    
    terms = {}
    
    for query in models.SearchQueryRecord.all().filter("time_stamp > ",
                                                       self.LAUNCH_DATE).run():
      count += 1
      
      if query.translated_query in self.CANNED_QUERIES:
        canned_count += 1
        continue
      
      parsed_query = parser.SearchQuery.ParseFromString(query.translated_query)
      
      for term in parsed_query.ExtractTerms():
        terms[term] = terms.get(term, 0) + 1
      
      if not query.results_count:
        no_results.append(query.translated_query)
      elif query.results_count > self.PAGE_SIZE:
        many_results.append((query.translated_query, query.results_count))
        
    many_results.sort(key=lambda r: r[1], reverse=True)
    ranked_terms = sorted(terms.items(), key=lambda r: r[1], reverse=True)[:20]
      
    self.response.out.write("Total queries: %d\n\n" % count)
    
    self.response.out.write("Example queries: %d (will be ignored in the analysis below)\n\n" % canned_count)
    
    self.response.out.write("%d queries with no results:\n" % len(no_results))
    pprint.pprint(no_results, self.response.out)
    self.response.out.write("\n")
    
    self.response.out.write("%d queries with many results (> 1 page):\n" % len(many_results))
    pprint.pprint(many_results, self.response.out)
    self.response.out.write("\n")
    
    self.response.out.write("Total number of terms found in queries: %d\n\n" % len(terms))
    self.response.out.write("Most popular terms (term, number of occurrences):\n")
    pprint.pprint(ranked_terms, self.response.out)
    self.response.out.write("\n")
    

class SitemapHandler(base_handler.BaseHandler):
  # TODO(bucur): Cache the site map in the blob store
  def get(self):
    course_keys = models.Course.all().fetch(None, keys_only=True)
    
    # TODO(bucur): Eliminate the /c hard-coding
    template_args = {
      "course_keys": course_keys,
      "url_prefix": "%s/c" % self.request.host_url
    }
    
    self.response.headers['Content-Type'] = 'application/xml'
    self.RenderTemplate('sitemap.xml', template_args)


class JSONSitemapHandler(base_handler.BaseHandler):
  # TODO(bucur): Cache the site map in the blob store
  def get(self):
    course_keys = models.Course.all().fetch(None, keys_only=True)
    data = ["%s/admin/c/%s.json" % (self.request.host_url, key) for key in course_keys]
    self.RenderJSON(data)
