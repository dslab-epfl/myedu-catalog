#!/usr/bin/env python

"""Administration tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import csv
import datetime
import json
import logging
import pprint
import re

from google.appengine.ext import db

from epfl.courses import base_handler
from epfl.courses import models
from epfl.courses.search import appsearch_admin as appsearch
from epfl.courses.search import parser


COURSES_DATA_FILE = "data/all_epfl_import.csv"
CRAWL_DATA_FILE = "data/crawler_import.json"

INVALID_SCIPER = 126096


def _BuildCourse(row):
  instructors = row["instructors"]
  if row["scipers"] and row["scipers"][0] == INVALID_SCIPER:
    instructors = ["multi"]
     
  return models.Course(
      title=row["title"],
      language=row["language"],
      instructors=instructors,
      sections=row["sections"],
      study_plans=row["study_plans"],
      urls=row["urls"])


def _SanitizeRow(row):
  def clean_up(field):
    return field.decode("utf-8").strip().replace("\n", "")
  def split_multiple(field):
    return map(lambda x: clean_up(x), field.split("#"))
  
  row["title"] = clean_up(row["title"])
  row["language"] = clean_up(row["language"])
  row["study_plans"] = split_multiple(row["study_plans"])
  
  if row["scipers"]:
    row["scipers"] = map(int, split_multiple(row["scipers"]))
    row["instructors"] = split_multiple(row["instructors"])
  else:
    row["scipers"] = []
    row["instructors"] = []
  
  row["sections"] = split_multiple(row["sections"])
  row["urls"] = split_multiple(row["urls"])


def ImportFromCSV(fs):
  reader = csv.DictReader(fs,
      ["_empty", "title", "language", "study_plans", "scipers", "instructors",
       "sections", "urls"])
  
  skip_flag = True
  
  empty_line_count = 0
  no_instructor_count = 0
  invalid_course_titles = []
  
  all_courses = []
  
  for row in reader:
    if not row["language"]:
      empty_line_count += 1
      continue
    if skip_flag:
      skip_flag = False
      continue
    
    try:
      _SanitizeRow(row)
      if not row["scipers"]:
        no_instructor_count += 1
      all_courses.append(_BuildCourse(row))
    except:
      raise
      invalid_course_titles.append(row["title"])
      
  logging.info("Created %d courses.\n" % len(all_courses))
  
  logging.info("Parsing stats: Empty lines: %d\n" 
               % empty_line_count)
  logging.info("Parsing stats: Unspecified instructor courses: %d\n" 
               % no_instructor_count)
  logging.info("Parsing stats: Invalid courses: %s\n" 
               % invalid_course_titles)
      
  return all_courses


def UpdateCourseInformation(course_list, course_data):
  course_dict = {}
  for course in course_list:
    course_dict[course.title] = course
    
  updated_count = 0
    
  for entry in course_data:
    course = course_dict.get(entry["title"])
    updated = False
    
    if not course:
      logging.warning("Could not find course '%s' when updating info" % entry["title"])
      continue
      
    for key, value in entry["info"].iteritems():
      if getattr(course, key) != value:
        setattr(course, key, value)
        course.needs_indexing_ = True
        updated = True
    if updated:
      updated_count += 1
      
  logging.info("Updated %d courses." % updated_count)
    

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
      data.append({
        "id": str(course.key()),
        "title": course.title,
        "language": course.language,
        "instructors": course.instructors,
        "sections": course.sections,
        "study_plans": course.study_plans,
        "urls": course.urls,
        "credit_count": course.credit_count,
        "coefficient": course.coefficient,
        "semester": course.semester,
        "exam_form": course.exam_form,
        "lecture_time": course.lecture_time,
        "lecture_weeks": course.lecture_weeks,
        "recitation_time": course.recitation_time,
        "recitation_weeks": course.recitation_weeks,
        "project_time": course.project_time,
        "project_weeks": course.project_weeks,
        "learning_outcomes": course.learning_outcomes,
        "content": course.content,
        "prior_knowledge": course.prior_knowledge,
        "type_of_teaching": course.type_of_teaching,
        "bibliography": course.bibliography,
        "keywords": course.keywords,
        "exam_form_detail": course.exam_form_detail,
        "note": course.note,
        "prerequisite_for": course.prerequisite_for,
        "library_recomm": course.library_recomm,
        "links": course.links
      })
    
    return data
      
  
  def get(self):
    if self.request.get("all"):
      data = self.DumpAll()
    else:
      data = self.DumpTitles()
    
    self.RenderJSON(data)


class ReinitDataHandler(base_handler.BaseHandler):
    
  def DeleteAllCourses(self):
    logging.info("Deleting all course information")
    course_keys = models.Course.all(keys_only=True).fetch(None)
    db.delete(course_keys)
    logging.info("Deleted %d courses.\n" % len(course_keys))
    
  def get(self):
    if self.request.get("rebuild"):
      self.DeleteAllCourses()
      with open(COURSES_DATA_FILE, "rU") as f:
        all_courses = ImportFromCSV(f)  
      db.put(all_courses)
      logging.info("Added %d courses.\n" % len(all_courses))
    else:
      all_courses = models.Course.all().fetch(None)
    
    with open(CRAWL_DATA_FILE, "r") as f:
      course_data = json.load(f, encoding="utf-8")
    
    UpdateCourseInformation(all_courses, course_data)
    
    db.put(all_courses)
    
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('OK.\n')
    
    
class BuildSearchIndexHandler(base_handler.BaseHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    
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
  
  @classmethod
  def ExtractTerms(cls, query_string):
    parsed_query = parser.SearchQuery.ParseFromString(query_string)
    
    terms = []
    
    for term in parsed_query.terms:
      terms.extend(re.findall(r"\w+", term, re.UNICODE))
    
    for _, value in parsed_query.filters:
      terms.extend(re.findall(r"\w+", value, re.UNICODE))
      
    return terms
  
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
      
      for term in self.ExtractTerms(query.translated_query):
        terms[term] = terms.get(term, 0) + 1
      
      if not query.results_count:
        no_results.append(query.translated_query)
      elif query.results_count > self.PAGE_SIZE:
        many_results.append((query.translated_query, query.results_count))
        
    many_results.sort(key=lambda r: r[1], reverse=True)
    ranked_terms = terms.items()[:20]
    ranked_terms.sort(key=lambda r: r[1], reverse=True)
      
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
