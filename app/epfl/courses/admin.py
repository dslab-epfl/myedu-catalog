#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Administrative tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import pprint

from epfl.courses import base_handler
from epfl.courses import config
from epfl.courses import models
from epfl.courses import static_data
from epfl.courses.search import appsearch_admin
from epfl.courses.search import parser

from google.appengine.ext import db


# SCIPER used to mark non-existent/multiple instructor
INVALID_SCIPER = 126096

COURSES_DATA_FILE = "data/consolidated_desc.json"


class ImportCourseCatalog(base_handler.BaseHandler):
  """Import the entire course catalog."""
  
  # The courses are imported in buckets of this size
  bucket_size = 100
  
  @staticmethod
  def PopulateSections():
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
                     master=section.master).put()
  
  @staticmethod
  def CreateCourse(course_desc):
    """Import a single course description."""
    
    # Create a new instance of a course, which will overwrite the old
    # one with the same key (if any).
    course = models.Course(key_name=course_desc["id"])
    
    # Set all the attributes
    course.title = course_desc["title"]
    course.language = course_desc["language"]
    
    sections = [e["section"] for e in course_desc["study_plan_entry"]]
    course.section_keys = [models.Section.get_by_key_name(section).key()
                           for section in sections]
    course.study_plans = [e["plan"] for e in course_desc["study_plan_entry"]]
    
    course.instructors = [i["name"] for i in course_desc["instructors"]]
    course.urls = [e["url"] for e in course_desc["study_plan_entry"]]
    
    course.credit_count = course_desc["credits"]
    course.coefficient = course_desc["coefficient"]
    
    course.semester = course_desc["semester"]
    course.exam_form = course_desc["exam_form"]
    
    hours_mapping = {
      "lecture": "lecture",
      "recitation": "recitation",
      "project": "project",
      "lab": "project",
      "practical": "project",
    }
    
    for src, dest in hours_mapping.iteritems():
      if not course_desc[src]:
        continue
      if "week_hours" in course_desc[src]:
        setattr(course, "%s_time" % dest,
                getattr(course, "%s_time" % dest) 
                + course_desc[src]["week_hours"])
        setattr(course, "%s_weeks" % dest, course_desc[src]["weeks"])
      elif "total_hours" in course_desc[src]:
        setattr(course, "%s_time" % dest,
                getattr(course, "%s_time" % dest) 
                + course_desc[src]["total_hours"])
        
    course.learning_outcomes = course_desc["free_text"].get("Learning outcomes")
    course.content = course_desc["free_text"].get("Content")
    course.prior_knowledge = course_desc["free_text"].get("Required prior knowledge")
    course.type_of_teaching = course_desc["free_text"].get("Type of teaching")
    course.bibliography = course_desc["free_text"].get("Bibliography and material")
    course.keywords = course_desc["free_text"].get("Keywords")
    course.exam_form_detail = course_desc["free_text"].get("Form of examination")
    course.note = course_desc["free_text"].get("Note")
    course.prerequisite_for = course_desc["free_text"].get("Prerequisite for")
    course.library_recomm = course_desc["library_recommends"]
    course.links = [link[1] for link in course_desc["links"]]
    
    course.needs_indexing_ = True
    
    return course
  
  @classmethod
  def ImportAllCourses(cls):
    """Import all courses found in the data file."""
    
    with open(COURSES_DATA_FILE, "r") as f:
      course_data = json.load(f, encoding="utf-8")
      
    course_bucket = []
    
    for course_desc in course_data["consolidations"]:
      course = cls.CreateCourse(course_desc)
      course_bucket.append(course)
      
      if len(course_bucket) == cls.bucket_size:
        db.put(course_bucket)
        course_bucket = []
        
    if course_bucket:
      db.put(course_bucket)
  
  def get(self):
    self.PopulateSections()
    self.ImportAllCourses()
    
    self.SetTextMode()
    self.response.out.write("OK.\n")
    

class SitemapHandler(base_handler.BaseHandler):
  # TODO(bucur): Cache the site map in the blob store
  def get(self):
    course_keys = models.Course.all().fetch(None, keys_only=True)
    
    template_args = {
      "course_keys": course_keys,
    }
    
    self.response.headers['Content-Type'] = 'application/xml'
    self.RenderTemplate('sitemap.xml', template_args)
    
    
class BuildSearchIndexHandler(base_handler.BaseHandler):
  def get(self):
    self.SetTextMode()
    
    if self.request.get("erase"):
      appsearch_admin.AppEngineIndex.ClearCourseIndex()
      self.response.out.write('OK.\n')
      return
    
    if self.request.get("rebuild"):
      courses = models.Course.all().fetch(None)
      appsearch_admin.AppEngineIndex.ClearIndexingStatus(courses)
    
    if appsearch_admin.AppEngineIndex.UpdateCourseIndex():
      self.response.out.write('OK.\n')
    else:
      self.response.out.write("Search quota exceeded. Try again later.\n")
      

class QueryStatsHandler(base_handler.BaseHandler):  
  
  def get(self):
    count = 0
    canned_count = 0
    
    no_results = []
    many_results = []
    
    terms = {}
    
    sample_queries = set([q[0] for q in config.SAMPLE_QUERIES])
    
    for query in models.SearchQueryRecord.all().filter("time_stamp > ",
                                                       config.LAUNCH_DATE).run():
      count += 1
      
      if query.translated_query in sample_queries:
        canned_count += 1
        continue
      
      parsed_query = parser.SearchQuery.ParseFromString(query.translated_query)
      
      for term in parsed_query.ExtractTerms():
        terms[term] = terms.get(term, 0) + 1
      
      if not query.results_count:
        no_results.append(query.translated_query)
      elif query.results_count > config.PAGE_SIZE:
        many_results.append((query.translated_query, query.results_count))
        
    many_results.sort(key=lambda r: r[1], reverse=True)
    ranked_terms = sorted(terms.items(), key=lambda r: r[1], reverse=True)[:20]
    
    self.SetTextMode()
      
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

