#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""AppEngine search."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging

from google.appengine.api import search
from google.appengine.runtime import apiproxy_errors

import unidecode

class AppSearchProvider(object):
  INDEX_NAME = 'courses-index'
  
  @classmethod
  def GetIndex(cls):
    return search.Index(name=cls.INDEX_NAME)
  
  @classmethod
  def GetQueryString(cls, query):
    return unidecode.unidecode(query.GetString(include_directives=False))
  
  @classmethod
  def Search(cls, query, results, limit=None, offset=None, accuracy=None):
    if isinstance(query, basestring):
      query_string = query
    else:
      query_string = cls.GetQueryString(query)
      
    results.latest_results = []
    
    try:
      search_query = search.Query(query_string,
                                  search.QueryOptions(limit=limit,
                                                      offset=offset,
                                                      number_found_accuracy=accuracy,
                                                      ids_only=True))
      search_results = cls.GetIndex().search(search_query)
      
      results.number_found = search_results.number_found
      results.latest_results = [document.doc_id for document in search_results.results]
      results.results.extend(results.latest_results)
    except apiproxy_errors.OverQuotaError:
      logging.error("Over quota error")
