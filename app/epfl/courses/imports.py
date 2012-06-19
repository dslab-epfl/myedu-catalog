#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""DB import code."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import csv
import json
import logging

from epfl.courses import models

from google.appengine.ext import db


COURSES_DATA_FILE = "data/all_epfl_import.csv"
CRAWL_DATA_FILE = "data/crawler_import.json"
RESTORATION_DATA_FILE = "data/restoration_import.json"

INVALID_SCIPER = 126096


################################################################################
# Original (EPFL XLS) Import
################################################################################

# TODO(bucur): Obsolete, rewrite

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


def _ImportFromCSV(fs):
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


def RebuildFromCSV():
  with open(COURSES_DATA_FILE, "rU") as f:
    all_courses = _ImportFromCSV(f)
    
  db.put(all_courses)
  
  return all_courses


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

