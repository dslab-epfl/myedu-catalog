#!/usr/bin/env python

"""Parses already crawled HTML files, and extracts course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import json
import logging
import os

COURSE_DESC_FILE = os.path.join(os.path.dirname(__file__),
                                'course_info.json')

def ParseHTMLData(html_data):
  pass

def main():
  logging.basicConfig(level=logging.INFO)
  
  course_data = None
  with open(COURSE_DESC_FILE, "r") as f:
    course_data = json.load(f, encoding="utf-8")
    
  if not course_data:
    logging.error("No course data found")
    return
  
  counters = {}
  
  for course in course_data:
    counters[course["id"]] = counters.get(course["id"], 0) + 1
    logging.info("Processing '%s'" % course["title"])
    
    html_data = None
    
    try:
      file_name = os.path.join(
          os.path.dirname(__file__),
          "html-data",
          "%s-%d.html" % (course["id"], counters[course["id"]]))
      
      with open(file_name, "r") as f:
        html_data = f.read()
    except IOError:
      logging.warning("Could not open the HTML file '%s'" % file_name)
      
    if html_data:
      ParseHTMLData(html_data)

if __name__ == "__main__":
  main()