#!/usr/bin/env python
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

# pylint: disable-msg=W0311

"""Consolidate course information in unique titles."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import logging
import os
import re
import unicodedata

import caching
import parse_study_plans as psp


this_dir = os.path.dirname(__file__)
consolidated_desc_path = os.path.join(this_dir, "consolidated_desc.json")


class ConsolidationError(Exception):
  pass


def _CanConsolidate(dest, src, append_set=None):
  for key, value in src.iteritems():
    # Ignore keys that are appended
    if append_set and key in append_set:
      continue
    # Consolidation is done recursively
    elif (key in dest and isinstance(value, dict)
          and isinstance(dest[key], dict)):
      if not _CanConsolidate(dest[key], value):
        return False
    elif key in dest and dest[key] != value:
      return False
    
  return True


def _ConsolidateDescription(dest, src, append_set=None, try_consolidate=True):
  """
  Add all keys in src to dest, according to some rules.
  
  If the key is in the append_set, the destination contains a list of
  all values consolidated for that key. Otherwise, the key is added to
  the destination if it doesn't exist there, or its value must match the
  value at destination.
  """
  
  # Raise first any exception, so we don't end up with incomplete consolidations
  if try_consolidate and not _CanConsolidate(dest, src, append_set):
    raise ConsolidationError("Cannot consolidate")
    
  for key, value in src.iteritems():
    if append_set and key in append_set:
      dest.setdefault(key, []).append(value)
    elif (key in dest and isinstance(value, dict)
          and isinstance(dest[key], dict)):
      _ConsolidateDescription(dest[key], value, try_consolidate=False)  
    elif key not in dest:
      dest[key] = value
      

def _CreateCourseID(title):
  """Create a course identifier based on its title."""
  
  if not title:
    return "untitled"

  # Convert accented characters as much as possible
  # http://stackoverflow.com/questions/5258623/remove-special-characters-from-string?lq=1
  title = unicodedata.normalize('NFKD', title).encode("ascii", "ignore")
  # Replace all non-alphanumerics with dashes
  title = re.sub(r"[\W-]+", "-", title)
  # Strip all trailing and ending dashes
  title = title.strip("-")
  # Lower-case everything
  return title.lower()


@caching.CachedJSON(consolidated_desc_path)
def ConsolidateCourseDescriptions(course_desc):
  title_dict = {}
  
  for course in course_desc["descriptions"]:
    title_dict.setdefault(course["en"]["title"], []).append(course)
    
  append_set = ["study_plan_entry"]
  
  consolidations = []
  cons_ids = set()
    
  for title in sorted(title_dict.keys()):
    logging.info("Processing title '%s'" % title)
    
    course_list = title_dict[title]
    
    # The consolidation list is built progressively.  We first try to add each
    # course to one of the existing consolidations.  If none is applicable, we
    # create a new consolidation.  We start with an empty list of
    # consolidations.
    
    cons_descriptions = []
    base_cons_id = _CreateCourseID(title)
    
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
        new_cons_id = base_cons_id
        id_counter = 2
        while new_cons_id in cons_ids:
          new_cons_id = "%s-%d" % (base_cons_id, id_counter)
          id_counter += 1
          
        new_cons = {
          "id": new_cons_id,
        }
        
        _ConsolidateDescription(new_cons, course, append_set)
        cons_descriptions.append(new_cons)
        cons_ids.add(new_cons_id)
        
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
  print len(set([course["en"]["title"] for course in course_desc["descriptions"]]))
  print "Consolidated titles:", len(consolidations["consolidations"])


if __name__ == "__main__":
  Main()
