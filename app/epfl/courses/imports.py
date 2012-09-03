#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""DB import code."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import logging

from epfl.courses import models

from google.appengine.ext import db


COURSES_DATA_FILE = "data/all_epfl_import.csv"
CRAWL_DATA_FILE = "data/crawler_import.json"
RESTORATION_DATA_FILE = "data/restoration_import.json"

INVALID_SCIPER = 126096



################################################################################
# Crawled course information
################################################################################


def _UpdateCourseInformation(course_list, course_data):
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


def UpdateCoursesFromCrawl(course_list):
  with open(CRAWL_DATA_FILE, "r") as f:
    course_data = json.load(f, encoding="utf-8")
    
  if not course_list:
    course_list = models.Course.all().fetch(None)
  
  _UpdateCourseInformation(course_list, course_data)
  db.put(course_list)

