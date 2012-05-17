#!/usr/bin/env python

"""Analyzes the parsed data."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import json
import logging
import os
import pprint
import re


PARSED_DATA_FILE = os.path.join(os.path.dirname(__file__),
                                'parser_output.json')


def AnalyzeSimpleFields(course_data):
  fields = {}
  
  for course in course_data:
    for key, value in course["info"].iteritems():
      if not value:
        continue
      if type(value) is list:
        value = value[0]
        
      fdict = fields.setdefault(key, {})
      fdict[value] = fdict.get(value, 0) + 1
      
  for key, value in fields.iteritems():
    if len(value) > 50:
      continue
    pprint.pprint([key, sum(value.values()), value])

def AnalyzeMissingData(course_data):
  missing_data = []
  
  complete_count = 0
  
  for course in course_data:
    missing_count = 0
    for value in course["info"].itervalues():
      if value is None:
        missing_count += 1
    
    if missing_count:   
      missing_data.append((course, missing_count))
    else:
      complete_count += 1
  missing_data.sort(key=lambda x: x[1], reverse=True)
  
  for course, missing_count in missing_data[:50]:
    if course["info"]["lecture_time"] and not course["info"]["recitation_time"]:
      print "***",
    
    print "%d/%d items missing at '%s'" % (missing_count, len(course["info"]), course["urls"])
    
  print "%d items are complete" % complete_count
  
def AnalyzeJahiaMarkup(course_data):
  markups = {}
  
  for course in course_data:
    for key in ["learning_outcomes", "prior_knowledge", "type_of_teaching",
                "form_of_examination", "bibliography"]:
      if key not in course["info"]:
        continue
      content = course["info"][key]
      if not content:
        continue
      
      for tag in re.findall(r"\[[^\[]*?\]", content):
        markups[tag] = markups.get(tag, 0) + 1
  
  pprint.pprint(markups)

def main():
  logging.basicConfig(level=logging.INFO)
  
  course_data = None
  with open(PARSED_DATA_FILE, "r") as f:
    course_data = json.load(f, encoding="utf-8")
    
  if not course_data:
    logging.error("No course data found")
    return
  
  AnalyzeMissingData(course_data)
  AnalyzeJahiaMarkup(course_data)
  AnalyzeSimpleFields(course_data)

if __name__ == "__main__":
  main()