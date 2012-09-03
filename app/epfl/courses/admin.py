#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Administrative tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json


# SCIPER used to mark non-existent/multiple instructor
INVALID_SCIPER = 126096

COURSES_DATA_FILE = "data/consolidated_desc.json"

from epfl.courses import base_handler
from epfl.courses import models
from epfl.courses import static_data

from google.appengine.ext import db


class ImportCourseCatalog(base_handler.BaseHandler):
  """Import the entire course catalog."""
  
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