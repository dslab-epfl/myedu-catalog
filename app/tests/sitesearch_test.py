#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Unit testing for query parser."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import pprint
import sys
import unittest

sdk_path = "/usr/local/google_appengine"
sys.path.insert(0, sdk_path)
import dev_appserver
dev_appserver.fix_sys_path()

from epfl.courses.search import SearchResults
from epfl.courses.search.parser import SearchQuery
from epfl.courses.search.sitesearch import SiteSearchProvider



def Main():
  logging.basicConfig(level=logging.INFO)
  query = SearchQuery.ParseFromString(sys.argv[1])
  results = SearchResults()
  SiteSearchProvider.Search(query, results)
  
  pprint.pprint(results.results)
  pprint.pprint(results.number_found)
  pprint.pprint(results.original_query)
  pprint.pprint(results.suggested_query)
  

if __name__ == "__main__":
  Main()