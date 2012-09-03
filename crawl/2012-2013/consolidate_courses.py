#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

# pylint: disable-msg=W0311

"""Consolidate course information in unique titles."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import logging
import os

import caching
import parse_study_plans as psp


this_dir = os.path.dirname(__file__)
consolidated_desc_path = os.path.join(this_dir, "consolidated_desc.json")


class ConsolidationError(Exception):
  pass


def _ConsolidateDescription(dest, src, append_set=None):
  """
  Add all keys in src to dest, according to some rules.
  
  If the key is in the append_set, the destination contains a list of
  all values consolidated for that key. Otherwise, the key is added to
  the destination if it doesn't exist there, or its value must match the
  value at destination.
  """
  
  # Raise first any exception, so we don't end up with incomplete consolidations
  for key, value in src.iteritems():
    if append_set and key in append_set:
      continue
    if key in dest and dest[key] != value:
      raise ConsolidationError("Cannot consolidate key '%s'" % key)
    
  for key, value in src.iteritems():
    if append_set and key in append_set:
      dest.setdefault(key, []).append(value)
      continue
      
    if key not in dest:
      dest[key] = value


@caching.CachedJSON(consolidated_desc_path)
def ConsolidateCourseDescriptions(course_desc):
  title_dict = {}
  
  for course in course_desc["descriptions"]:
    title_dict.setdefault(course["title"], []).append(course)
    
  append_set = set(["url", "study_plan_entry"])
  
  consolidations = []
    
  for title, course_list in title_dict.iteritems():
    logging.info("Processing title '%s'" % title)
    
    # The consolidation list is built progressively.  We first try to add each
    # course to one of the existing consolidations.  If none is applicable, we
    # create a new consolidation.  We start with an empty list of
    # consolidations.
    
    cons_descriptions = []
    
    for course in course_list:
      success = False
      
      for cons_desc in cons_descriptions:
        try:
          _ConsolidateDescription(cons_desc, course, append_set)
          success = True
          break
        except ConsolidationError:
          continue
    
      if not success:
        new_cons = {}
        _ConsolidateDescription(new_cons, course, append_set)
        cons_descriptions.append(new_cons)
        
    logging.info("Title '%s' x %d consolidated in %d descriptions"
                 % (title, len(course_list), len(cons_descriptions)))
    
    if len(cons_descriptions) > 1:
      for course in course_list:
        logging.info("URL: %s" % course["study_plan_entry"]["url"])
    
    consolidations.extend(cons_descriptions)
    
  return {
    "consolidations": consolidations,
  }


def Main():
  logging.basicConfig(level=logging.INFO)
  
  study_plans = psp.FetchStudyPlans()
  courses = psp.FetchCourseList(study_plans)
  course_desc = psp.FetchCourseDescriptions(courses)
  
  consolidations = ConsolidateCourseDescriptions(course_desc)
  
  print "Total course descriptions:", len(course_desc["descriptions"])
  print "Unique course titles:",
  print len(set([course["title"] for course in course_desc["descriptions"]]))
  print "Consolidated titles:", len(consolidations["consolidations"])


if __name__ == "__main__":
  Main()
