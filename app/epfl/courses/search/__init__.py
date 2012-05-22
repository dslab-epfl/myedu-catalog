#!/usr/bin/env python

"""The search infrastructure for the course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import os
import StringIO
from xml.etree import ElementTree
import urllib

from google.appengine.api import search
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from epfl.courses import models

import unidecode


class SearchQuery(object):
  def __init__(self, query=None, filters=None, options=None):
    self.query = query or []
    self.filters = filters or []
    self.options = None
    
  @classmethod
  def BuildFromRequest(cls, request):
    def append_filter(query, id_name, field_name):
      field_value = request.get(id_name)
      if field_value:
        query.filters.append((field_name, field_value))
        
    query = cls(query=request.get("q", "").split())
    
    append_filter(query, "aq_t", "title")
    append_filter(query, "aq_lang", "language")
    append_filter(query, "aq_in", "instructor")
    append_filter(query, "aq_sec", "section")
    append_filter(query, "aq_sem", "semester")
    append_filter(query, "aq_exam", "exam")
    append_filter(query, "aq_cred", "credits")
    append_filter(query, "aq_coeff", "coefficient")
    
    append_filter(query, "aq_hours_l", "lecthours")
    append_filter(query, "aq_hours_r", "recithours")
    append_filter(query, "aq_hours_p", "projhours")
    
    return query
  
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
    main_query = " ".join(query.query)
    filters = " ".join('%s:"%s"' % (x[0], x[1]) for x in query.filters)
    return " ".join([main_query, filters]).strip()
  
  @classmethod
  def Search(cls, query_string, limit=None, offset=None, accuracy=None):
    try:
      query = search.Query(unidecode.unidecode(query_string),
                           search.QueryOptions(limit=limit,
                                               offset=offset,
                                               number_found_accuracy=accuracy,
                                               ids_only=True))
      search_results = cls.GetIndex().search(query)
    
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
    main_query = " ".join(query.query)
    filters = " ".join('"%s"' % x[1] for x in query.filters)
    return " ".join([main_query, filters]).strip()

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
    
    if suggestion_node is not None:
      return cls.Search(SearchQuery([suggestion_node.get("q")]),
                        limit, offset, accuracy,
                        xml_data.find("Q").text)
    
    number_found_node = xml_data.find("RES/M")
    
    if number_found_node is None:
      return
      
    number_found = int(number_found_node.text)
    
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

