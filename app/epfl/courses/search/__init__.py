#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""The search infrastructure for the course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import logging

from parser import SearchQuery
from appsearch import AppSearchProvider
from sitesearch import SiteSearchProvider


class SearchResults(object):
  def __init__(self, original_query=None, offset=None):
    self.original_query = original_query
    self.suggested_query = None
    
    self.results = []
    self.latest_results = []
    
    self.number_found = None
    self.offset = offset
    
    self.original_url_ = None


class AutocorrectedSearchProvider(object):
  def __init__(self, provider, exact_search=False):
    self.provider = provider
    self.original_query = None
    self.suggested_query = None
    self.exact_search = exact_search
    
  def Search(self, query, search_results, limit=None, offset=None,
             accuracy=None):
    query_string = query.GetString()
    
    logging.info("Searching for original query using '%s'" % self.provider)
    self.provider.Search(query,
                         search_results,
                         limit=limit,
                         offset=offset,
                         accuracy=accuracy)
    
    self.suggested_query = search_results.suggested_query
    
    if (not search_results.number_found and search_results.suggested_query
        and not self.exact_search):
      logging.info("Searching for autosuggested query using '%s' % self.provider")
      self.original_query = query_string
      self.provider.Search(search_results.suggested_query,
                           search_results,
                           limit=limit,
                           offset=offset,
                           accuracy=accuracy)


class StagedSearchProvider(object):
  def __init__(self, providers, use_all=False):
    self.providers = providers
    self.use_all = use_all
    
  def Search(self, query, search_results, limit=None, offset=None,
             accuracy=None):
    for provider in self.providers:
      logging.info("Searching using stage %s" % provider)
      provider.Search(query,
                      search_results,
                      limit=limit,
                      offset=offset,
                      accuracy=accuracy)
      if search_results.number_found and not self.use_all:
        break
