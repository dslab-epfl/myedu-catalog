#!/usr/bin/env python

"""Administration tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import csv
import jinja2
import json
import logging
import os
import pprint
import webapp2

from google.appengine.ext import db

from epfl.courses import models
from epfl.courses import search


COURSES_DATA_FILE = "data/all_epfl_import.csv"
CRAWL_DATA_FILE = "data/crawler_import.json"

INVALID_SCIPER = 126096

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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
    

class DumpHandler(webapp2.RequestHandler):
  """Shamelessly dumps the entire course information."""
  def get(self):
    results = models.Course.all().run(projection=('title', 'urls'))
    
    data = [{ "id": str(course.key()), "title": course.title, "urls": course.urls[0]}
            for course in results]
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(data, indent=True, encoding="utf-8"))


class ReinitDataHandler(webapp2.RequestHandler):
    
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
    
    
class BuildSearchIndexHandler(webapp2.RequestHandler):

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    
    if self.request.get("erase"):
      search.AppEngineSearch.ClearCourseIndex()
      self.response.out.write('OK.\n')
      return
    
    if self.request.get("rebuild"):
      courses = models.Course.all().fetch(None)
      search.AppEngineSearch.ClearIndexingStatus(courses)
    
    if search.AppEngineSearch.UpdateCourseIndex():
      self.response.out.write('OK.\n')
    else:
      self.response.out.write("Search quota exceeded. Try again later.\n")


class StatsHandler(webapp2.RequestHandler):
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

class SitemapHandler(webapp2.RequestHandler):
  # TODO(bucur): Cache in the blob store the sitemap
  def get(self):
    course_keys = models.Course.all().fetch(None, keys_only=True)
    
    # TODO(bucur): Eliminate the /c hard-coding
    template_args = {
      "course_keys": course_keys,
      "url_prefix": "%s/c" % self.request.host_url
    }
    
    template = jinja_environment.get_template('sitemap.xml')
    
    self.response.headers['Content-Type'] = 'application/xml'
    self.response.out.write(template.render(template_args))
