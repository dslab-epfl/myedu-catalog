#!/usr/bin/env python

"""Crawl EPFL IS-Academia's course books."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import json
import logging
import os
import urllib

DATA_FILE = os.path.join(os.path.dirname(__file__),
                         'course_info.json')

COURSE_BOOK_BASE_URL = "http://isa.epfl.ch/imoniteur_ISAP/!GEDPUBLICREPORTS.txt\
?ww_i_reportModel=83782576&ww_i_reportModelXsl=83782665\
&ww_x_MAT=%d&ww_x_PERIODE_ACAD=%d&ww_x_SECTION=%d&ww_x_BLOC=%d"

COURSE_BOOK_BASE_URL_ALT = "http://isa.epfl.ch/imoniteur_ISAP/!GEDPUBLICREPORTS.txt\
?ww_i_reportModel=5059249&ww_i_reportModelXsl=5059315\
&ww_x_MAT=%d&ww_x_PROGRAMME=%d"

def GetCourseBookURL(course_url):
  url_params = dict([pair.split("=") 
                     for pair in course_url.split("?")[1].split("&")])
  
  course_book_url = None
  if url_params['ww_i_niveau']:
    course_book_url = COURSE_BOOK_BASE_URL % (
      int(url_params['ww_i_matiere']),
      int(url_params['ww_x_anneeacad']),
      int(url_params['ww_i_section']),
      int(url_params['ww_i_niveau'])
    )
  else:
    course_book_url = COURSE_BOOK_BASE_URL_ALT % (
      int(url_params['ww_i_matiere']),
      int(url_params['ww_i_section'])
    )
    
  return course_book_url

def main():
  logging.basicConfig(level=logging.INFO)
  
  course_data = None
  with open(DATA_FILE, "r") as f:
    course_data = json.load(f, encoding="utf-8")
    
  if not course_data:
    logging.error("No course data found")
    return
  
  counters = {}
  
  for course in course_data:
    counters[course["id"]] = counters.get(course["id"], 0) + 1
    
    logging.info("Processing '%s'" % course["title"])
    
    url_handle = urllib.urlopen(course["urls"])
    url_data = url_handle.read()
    with open(os.path.join(os.path.dirname(__file__),
                           "%s-%d.html" % (course["id"], counters[course["id"]])), "w") as f:
      f.write(url_data)

    url_handle.close()


if __name__ == "__main__":
  main()