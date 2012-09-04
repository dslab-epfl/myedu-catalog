#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Google Site Search provider."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import contextlib
import logging
import unittest
import urllib
import urllib2
from xml.etree import ElementTree

from epfl.courses import config


class SiteSearchProvider(object):
  SEARCH_URL = "http://www.google.com/search?hl=en&q=%s&ie=utf8&oe=utf8&client=google-csbe&output=xml_no_dtd&cx=%s"
  
  FILTER_MAPPING = {
    'title': "title",
    'language': "language",
    'instructor': "instructor",
    'section': "sections",
    'plan': '"study plans"',
    'credits': '"ects credits"',
    'coefficient': "coefficient",
    'semester': "semester",
    'exam': "exam",
    'lecthours': '"ects credits"',
    'recithours': '"ects credits"',
    'projhours': '"ects credits"',
    'practhours': '"ects credits"',
    'outcomes': '"learning outcomes"',
    'content': "content",
    'prereq': '"prior knowledge"',
    'teaching': '"type of teaching"',
    'biblio': "bibliography",
    'keywords': "keywords",
    'examdetail': '"form of examination"',
    'note': "note",
    'prereqfor': '"prerequisite for"',
    'libraryrec': '"library recommends"',
    'links': "links",
  }
  
  def __init__(self, avoid_fields=None):
    self.avoid_fields = avoid_fields or ["language", "section", "plan",
                                         "credits", "coefficient", "semester",
                                         "exam", "lecthours", "recithours",
                                         "projhours", "practhours"]
    
  
  @classmethod
  def GetQueryStringFuzzy(cls, query):
    query_string = []
    if query.filters:
      query_string.append(" ".join(["%s: %s" % (cls.FILTER_MAPPING.get(key, key), value)
                                    for key, value in query.filters]))
    if query.terms:
      query_string.append(" ".join(query.terms))
      
    return " ".join(query_string)
  
  @classmethod
  def EscapeQueryString(cls, query_string):
    return urllib.quote_plus(query_string.encode("utf-8"))
  
  @classmethod
  def GetSearchURL(cls, query, limit=None, offset=None):
    if isinstance(query, basestring):
      query_string = query
    else:
      query_string = cls.GetQueryStringFuzzy(query)

    escaped_query = cls.EscapeQueryString(query_string)
    
    url = cls.SEARCH_URL % (escaped_query, config.SEARCH_ENGINE_ID)
    if limit:
      url += "&num=%d" % limit
    if offset:
      url += "&start=%d" % offset
      
    return url
  
  @classmethod
  def _ExtractCourseList(cls, xml_data, results):
    results.latest_results = []
    
    number_found_node = xml_data.find("RES/M")
    if number_found_node is None:
      logging.info("No search results found")
      return
    results.number_found = int(number_found_node.text)
    
    logging.info("%d search results found" % results.number_found)
    
    new_offset = None
    
    for result in xml_data.findall("RES/R"):
      if new_offset is None:
        new_offset = int(result.get("N")) - 1
      
      course_url = result.find("U").text.strip()
      course_key = course_url.rsplit("/", 1)[1]
      results.latest_results.append(course_key)
      
    if new_offset is not None:
      results.offset = new_offset
      
    results.results.extend(results.latest_results)
  
  @classmethod
  def _ExtractSuggestion(cls, xml_data, results):
    suggestion_node = xml_data.find("Spelling/Suggestion")
    if suggestion_node is not None:
      results.suggested_query = suggestion_node.get("q")

  def Search(self, query, results, limit=None, offset=None, accuracy=None):
    if not isinstance(query, basestring) and query.filters:
      for key, _ in query.filters:
        if key in self.avoid_fields:
          logging.info("Rejecting query as containing avoided fields")
          return

    # Compose the search URL    
    url = self.GetSearchURL(query, limit, offset)
    logging.info("Performing GSS query at '%s'" % url)
    results.original_url_ = url
    
    # Perform the query
    with contextlib.closing(urllib2.urlopen(url)) as f:
      data = f.read()
      
      if f.getcode() != 200:
        logging.warning("Could not obtain search results from GSS")
        return

      xml_data = ElementTree.fromstring(data)
      logging.debug("XML data: %s" % ElementTree.tostring(xml_data))
      
    self._ExtractCourseList(xml_data, results)
    self._ExtractSuggestion(xml_data, results)


if __name__ == "__main__":
  unittest.main()