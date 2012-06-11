#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""The search infrastructure for the course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

from parser import SearchQuery
from appsearch import AppSearchProvider
from sitesearch import SiteSearchProvider


class SearchResults(object):
  def __init__(self, original_query=None):
    self.original_query = original_query
    self.suggested_query = None
    
    self.results = []
    self.latest_results = []
    
    self.number_found = None
    
    self.original_url_ = None
