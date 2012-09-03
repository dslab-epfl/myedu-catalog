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

from google.appengine.ext import db


class ImportCourseCatalog(base_handler.BaseHandler):
  """Import the entire course catalog."""
  
  @staticmethod
  def ImportCourse(course_desc):
    """Import a single course description."""
    
    # Create a new instance of a course, which will overwrite the old
    # one with the same key (if any).
    course = models.Course(key_name=course_desc["id"])
    
    # Set all the attributes
    course.title = course_desc["title"]
    course.language = course_desc["language"]
    
    # TODO(bucur): Sections and study plans
    
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
    # Now commit everything...
    course.put()
  
  @staticmethod
  def ImportAllCourses():
    """Import all courses found in the data file."""
    
    with open(COURSES_DATA_FILE, "r") as f:
      course_data = json.load(f, encoding="utf-8")
    
    for course_desc in course_data["consolidations"]:
      ImportCourseCatalog.ImportCourse(course_desc)
  
  def get(self):
    self.ImportAllCourses()
    
    self.SetTextMode()
    self.response.out.write("OK.\n")