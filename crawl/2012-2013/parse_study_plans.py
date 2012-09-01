#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Parse the 2012-2013 course descriptions starting from study plan URLs."""

__author__ = "stefan.bucur@epfl.ch"

import contextlib
import json
import os
import urllib
import urlparse


from bs4 import BeautifulSoup

# The root of our parsing
search_base_url = "http://search-test.epfl.ch"
study_plans_url = urlparse.urljoin(search_base_url, "/eduweb.action")

this_dir = os.path.dirname(__file__)
study_plans_path = os.path.join(this_dir, "study_plans.json")
course_list_path = os.path.join(this_dir, "course_list.json")


# CACHING UTILITIES

def CachedJSON(file_name):
  """Decorator factory that caches the result of a function in a JSON file."""
  
  def decorator(func):
    def wrapper(*args, **kwargs):
      try:
        with open(file_name, "r") as f:
          data = json.load(f, encoding="utf-8")
        print "-- Found cached data at '%s'" % file_name
        return data
      except IOError:
        pass
      
      print "-- Data not found at '%s'. Computing." % file_name
      data = func(*args, **kwargs)
      
      try:
        with open(file_name, "w") as f:
          json.dump(data, f, indent=True, encoding="utf-8")
        print "-- Saved computed data at '%s'" % file_name
      except IOError:
        print "-- Could not save computed data at '%s'" % file_name
      
      return data
    
    return wrapper
  return decorator


def CachedURLGet(url):
  """Read and cache the contents of a URL."""
  
  # Construct the file name of the cache
  parsed_url = urlparse.urlsplit(url)
  parsed_url_path = parsed_url.path.lstrip("/")
  if parsed_url.query:
    parsed_url_path += "?" + parsed_url.query
    
  cache_file_name = os.path.join(this_dir, parsed_url.netloc, parsed_url_path)
  
  try:
    with open(cache_file_name, "r") as f:
      data = f.read()
    print "-- URL cache found for %s [%s]" % (url, cache_file_name)
    return data
  except IOError:
    pass
  
  print "-- URL not cached. Retrieving %s" % url
  
  with contextlib.closing(urllib.urlopen(url)) as f:
    data = f.read()
    
  try:
    try:
      os.makedirs(os.path.dirname(cache_file_name))
    except OSError:
      pass
    
    with open(cache_file_name, "w") as f:
      f.write(data)
    print "-- Saved URL data for %s [%s]" % (url, cache_file_name)
  except IOError:
    print "-- Could not save cache for URL %s at %s" % (url, cache_file_name)
  
  return data


def _ProcessStudyPlan(plan_id, plan_name, plan_soup, id_trim_size=3):
  sections = []
  for list_item in plan_soup.find_all('li'):
    section_id = "-".join(list_item['id'].split("_")[id_trim_size:]).upper()
    section_title = list_item.a.string
    section_url = search_base_url + list_item.a["href"]
    
    print section_id, section_title, section_url
    
    sections.append({
      "id": section_id,
      "title": section_title,
      "url": section_url,
    })
    
  return {
    "id": plan_id,
    "name": plan_name,
    "sections": sections,
  }


@CachedJSON(study_plans_path)
def FetchStudyPlans():
  study_plans_html = CachedURLGet(study_plans_url)
    
  plans = []
    
  soup = BeautifulSoup(study_plans_html)
  # Propedeutics
  prop_sections = soup.find('li', id='bama_prop')
  plans.append(_ProcessStudyPlan("prop", "Propedeutics", prop_sections))
  
  # Bachelor
  bachelor_sections = soup.find('li', id='bama_cyclebachelor')
  plans.append(_ProcessStudyPlan("bachelor", "Bachelor", bachelor_sections))
  
  # Master
  master_sections = soup.find('li', id='bama_cyclemaster')
  plans.append(_ProcessStudyPlan("master", "Master", master_sections))
  
  # Doctoral
  phd_sections = soup.find('li', id='edoc')
  plans.append(_ProcessStudyPlan("edoc", "Doctoral", phd_sections,
                                 id_trim_size=2))
  
  # Minor
  minor_sections = soup.find('li', id='min_')
  plans.append(_ProcessStudyPlan("min", "Minor", minor_sections))
  
  return {
    "plans": plans
  }
  

def _FetchCoursesInSection(section_url):
  section_html = CachedURLGet(section_url)
    
  soup = BeautifulSoup(section_html)
  

@CachedJSON(course_list_path)
def FetchCourseList(study_plans):
  for plan in study_plans["plans"]:
    for section in plan["sections"]:
      _FetchCoursesInSection(section["url"])


def Main():
  study_plans = FetchStudyPlans()
  FetchCourseList(study_plans)
  


if __name__ == "__main__":
  Main()