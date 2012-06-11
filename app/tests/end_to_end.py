#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""End-to-end testing of MyEdu search functionality."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import contextlib
import logging
import re
import urllib2

import bs4


app_url = "http://%d.courses-epfl.appspot.com/catalog?q=%s"
app_version = 7


class FailedTestException(Exception):
  def __init__(self, param, expected, actual):
    message = "Mismatched %s: expected '%s', got '%s'" % (param, expected, actual)
    Exception.__init__(self, message)

class TestScenario(object):
  results_re = re.compile("Showing results\s+(\d+)-(\d+)\s+out of\s+(\d+)")
  
  def __init__(self, query, expected_count=None):
    self.query = query
    self.expected_count = expected_count
    
  def _ExtractResultsCount(self, soup):
    results_text = soup.find(attrs={ "class": "info_box" })
    if results_text:
      results_text = results_text.text.strip()
    else:
      return 0
    
    match = self.results_re.match(results_text)
    return int(match.group(3))
    
  def Execute(self):
    logging.info("Processing query '%s'" % self.query)
    
    url = app_url % (app_version, urllib2.quote(self.query))
    logging.info("Generated URL: %s" % url)
    
    with contextlib.closing(urllib2.urlopen(url)) as f:
      soup = bs4.BeautifulSoup(f.read())
    
    if self.expected_count is not None:
      count = self._ExtractResultsCount(soup)
      if count < self.expected_count:
        raise FailedTestException("count", self.expected_count, count)
    
test_scenarios = [
  TestScenario("desbioles", expected_count=3),
  TestScenario("programing"),
  TestScenario("cristoph koch", expected_count=1),
  TestScenario("algaebra", expected_count=17),
  TestScenario("mathematiques"),
  TestScenario("morret"),
  TestScenario("hubax"),
  TestScenario("rudiger"),
  TestScenario("chappelier"),
  TestScenario("kostik"),
  TestScenario("cadnea"),
  TestScenario("andre"),
  TestScenario("matematics"),
  TestScenario("susstrunk", expected_count=2),
  TestScenario("Mathématiques", expected_count=2),
  # Links coming from course pages
  
]

def Main():
  logging.basicConfig(level=logging.INFO)
  
  for test_scenario in test_scenarios:
    try:
      test_scenario.Execute()
    except FailedTestException as e:
        logging.error("Failed test: %s" % e)

if __name__ == "__main__":
  Main()