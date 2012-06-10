#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""The search infrastructure for the course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import os
import re
import StringIO
from xml.etree import ElementTree
import urllib

from google.appengine.api import search
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from epfl.courses import models
from epfl.courses.search import parser

import unidecode


class SearchQueryOptions(object):
  CORPUS_GSS = 0
  CORPUS_DB = 1
  CORPUS_INDEX = 2
  
  def __init__(self, exact=False,
               corpus=CORPUS_GSS):
    self.exact = exact
    self.corpus = corpus


class SearchResults(object):
  def __init__(self, results, number_found, query=None, original=None):
    self.results = results
    self.number_found = number_found
    self.query = query
    self.original = original


class AppSearchProvider(object):
  INDEX_NAME = 'courses-index'
  
  @classmethod
  def GetIndex(cls):
    return search.Index(name=cls.INDEX_NAME)
  
  @classmethod
  def GetQueryString(cls, query):
    return query.GetString(include_directives=False)
  
  @classmethod
  def Search(cls, query, limit=None, offset=None, accuracy=None):
    query_string = cls.GetQueryString(query)
    
    try:
      search_query = search.Query(unidecode.unidecode(query_string),
                                  search.QueryOptions(limit=limit,
                                                      offset=offset,
                                                      number_found_accuracy=accuracy,
                                                      ids_only=True))
      search_results = cls.GetIndex().search(search_query)
    
      return SearchResults([document.doc_id for document in search_results.results],
                           search_results.number_found)
    except apiproxy_errors.OverQuotaError:
      logging.error("Over quota error")
      return None
