#!/usr/bin/env python

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


class SiteSearchProvider(object):
  SEARCH_ENGINE_ID = "000528554756935640955:t5p6oxkfane"
  SEARCH_URL = "http://www.google.com/search?q=%s&&client=google-csbe&output=xml_no_dtd&cx=%s"
  
  @classmethod
  def GetQueryString(cls, query):
    return query.GetString(include_directives=False)

  @classmethod
  def Search(cls, query, limit=None, offset=None, accuracy=None, original=None):
    query_string = cls.GetQueryString(query)
    escaped_query = urllib.quote_plus(unidecode.unidecode(query_string))
    
    url = cls.SEARCH_URL % (escaped_query, cls.SEARCH_ENGINE_ID)
    if limit:
      url += "&num=%d" % limit
    if offset:
      url += "&start=%d" % offset
    
    u = urlfetch.fetch(url)
    if u.status_code != 200:
      logging.warning("Could not obtain search results from GSS")
      return
    
    xml_data = ElementTree.parse(StringIO.StringIO(u.content))
    
    course_list = []
    
    suggestion_node = xml_data.find("Spelling/Suggestion")
    
    if suggestion_node is not None and original is None:
      logging.info("Searching instead for autosuggested %s" % suggestion_node.get("q"))
      return cls.Search(parser.SearchQuery.ParseFromString(suggestion_node.get("q")),
                        limit, offset, accuracy,
                        xml_data.find("Q").text)
    
    number_found_node = xml_data.find("RES/M")
    
    if number_found_node is None:
      logging.info("No search results found using query '%s'" % escaped_query)
      return
      
    number_found = int(number_found_node.text)
    
    logging.info("%d search results found" % number_found)
    
    for result in xml_data.findall("RES/R"):
      if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
        for attr in result.findall("PageMap/DataObject/Attribute"):
          if attr.get("name") == "title":
            course_title = attr.text
            course_key = models.Course.all().filter("title = ", course_title).get(keys_only=True)
            if course_key:
              course_list.append(course_key)
      else:
        course_url = result.find("U").text.strip()
        url_tokens = course_url.split("/")
        if url_tokens[-2] != "c":
          continue
        course_key = url_tokens[-1]
        course_list.append(course_key)
      
    return SearchResults(course_list, number_found,
                         xml_data.find("Q").text, original)
