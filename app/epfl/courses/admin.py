#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Administrative tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import logging
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
  
  # Mappings to read from the right free text descriptions. Keys are course
  # attributes, and values are the titles as parsed from ISA URLs.
  free_text_map = {
    "en": {
      "learning_outcomes": "Learning outcomes",
      "content": "Content",
      "prior_knowledge": "Required prior knowledge",
      "type_of_teaching": "Type of teaching",
      "bibliography": "Bibliography and material",
      "keywords": "Keywords",
      "exam_form_detail": "Form of examination",
      "note": "Note",
      "prerequisite_for": "Prerequisite for",
    },
    "fr": {
      "learning_outcomes": u"Objectifs d'apprentissage",
      "content": u"Contenu",
      "prior_knowledge": u"Prérequis",
      "type_of_teaching": u"Forme d'enseignement",
      "bibliography": u"Bibliographie et matériel",
      "keywords": u"Mots clés",
      "exam_form_detail": u"Forme du contrôle",
      "note": u"Remarque",
      "prerequisite_for": u"Préparation pour",
    }
  }
  
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
                     alias=section.alias).put()
                     
  @staticmethod
  def ResolveSectionKeys(section_key_names):
    """Compute the set of keys after resolving all aliases."""
    
    sections = [models.Section.get_by_key_name(section)
                for section in section_key_names]
    
    aliased_key_names = [(section.alias if section.alias
                          else section.key().name())
                         for section in sections]
    
    return [models.Section.get_by_key_name(section).key()
            for section in aliased_key_names]
  
  @classmethod
  def CreateCourse(cls, course_desc, language):
    """Import a single course description."""
    
    # Create a new instance of a course, which will overwrite the old
    # one with the same key (if any).
    course_desc_lang = course_desc[language]
    course_key_name = "%s:%s" % (language, course_desc["id"])
    course = models.Course(key_name=course_key_name)
    course.desc_language_ = language
    
    # Set all the attributes
    course.title = course_desc_lang["title"]
    course.language = course_desc_lang["language"]
    
    section_keys = cls.ResolveSectionKeys(
      [e["section"] for e in course_desc["study_plan_entry"]])
    course.section_keys = section_keys
    
    course.study_plans = [e["plan"] for e in course_desc["study_plan_entry"]]
    course.code_prefix = [(e["code"][0]
                           if e["code"][0] else "XX")
                          for e in course_desc["study_plan_entry"]]
    course.code_number = [(e["code"][1]
                           if e["code"][0] else "000")
                          for e in course_desc["study_plan_entry"]]
    
    course.instructors = [i["name"]
                          for i in course_desc_lang["instructors"]]
    if language == "en":
      course.urls = [e["url"] for e in course_desc["study_plan_entry"]]
    else:
      course.urls = [e["url_fr"] for e in course_desc["study_plan_entry"]]
    
    course.credit_count = course_desc_lang["credits"]
    course.coefficient = course_desc_lang["coefficient"]
    
    course.semester = course_desc_lang["semester"]
    course.exam_form = course_desc_lang["exam_form"]
    
    hours_mapping = {
      "lecture": "lecture",
      "recitation": "recitation",
      "project": "project",
      "lab": "project",
      "practical": "project",
    }
    
    for src, dest in hours_mapping.iteritems():
      if not course_desc_lang[src]:
        continue
      if "week_hours" in course_desc_lang[src]:
        setattr(course, "%s_time" % dest,
                getattr(course, "%s_time" % dest) 
                + course_desc_lang[src]["week_hours"])
        setattr(course, "%s_weeks" % dest, course_desc_lang[src]["weeks"])
      elif "total_hours" in course_desc_lang[src]:
        setattr(course, "%s_time" % dest,
                getattr(course, "%s_time" % dest) 
                + course_desc_lang[src]["total_hours"])
        
    course.library_recomm = course_desc_lang["library_recommends"]
    course.links = [link[1] for link in course_desc_lang["links"]]
    
    for attr, title in cls.free_text_map[language].iteritems():
      setattr(course, attr, course_desc_lang["free_text"].get(title))
    
    course.needs_indexing_ = True
    
    return course
  
  @classmethod
  def ImportAllCourses(cls, language):
    """Import all courses found in the data file."""

    with open(COURSES_DATA_FILE, "r") as f:
      course_data = json.load(f, encoding="utf-8")
      
    course_bucket = []
    
    for course_desc in course_data["consolidations"]:
      try:
        course = cls.CreateCourse(course_desc, language)
        course_bucket.append(course)
        
        if len(course_bucket) >= cls.bucket_size:
          db.put(course_bucket)
          course_bucket = []
      except:
        logging.error("Error in processing course %s in language %s"
                      % (course_desc["id"], language))
        raise
        
    if course_bucket:
      db.put(course_bucket)
  
  def get(self, operation):
    if operation not in ["en", "fr", "sections"]:
      self.abort(400)
      
    self.PopulateSections()
    if operation in ["en", "fr"]:
      self.ImportAllCourses(operation)
    
    self.SetTextMode()
    self.response.out.write("OK (%s).\n" % operation)
    

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
  def get(self, operation):
    self.SetTextMode()
    
    if operation == "erase":
      appsearch_admin.AppEngineIndex.ClearCourseIndex()
      self.response.out.write('OK.\n')
      return
    
    if operation == "rebuild":
      courses = models.Course.all().fetch(None)
      appsearch_admin.AppEngineIndex.ClearIndexingStatus(courses)
    
    if operation == "update" or operation == "rebuild":
      if appsearch_admin.AppEngineIndex.UpdateCourseIndex():
        self.response.out.write('OK.\n')
      else:
        self.response.out.write("Search quota exceeded. Try again later.\n")
    else:
      self.abort(400)
      

class RemoveSectionHandler(base_handler.BaseHandler):
  def get(self, sec_id, dest_id):
    self.SetTextMode()
    
    section = models.Section.get_by_key_name(sec_id)
    destination = models.Section.get_by_key_name(dest_id)
    
    if section is None or destination is None:
      self.abort(400)
      
    courses = []
      
    for course in models.Course.all().filter("section_keys =", section.key()):
      course.needs_indexing_ = True
      
      course.section_keys = map(lambda key: destination.key()
                                if key == section.key() else key,
                                course.section_keys)
      
      section_set = set(course.section_keys)
      section_set.remove(section.key())
      section_set.add(destination.key())
      
      course.section_keys = list(section_set)
      courses.append(course)
      
    self.response.out.write("Affected courses: %d...\n" % len(courses))
    
    db.put(courses)
    
    section.delete()
    
    self.response.out.write("OK. The search index needs to be rebuilt.")
      

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

