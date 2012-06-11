#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Google Site Search provider."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import contextlib
import logging
import unittest
import urllib
from xml import etree


class SiteSearchProvider(object):
  SEARCH_ENGINE_ID = "000528554756935640955:t5p6oxkfane"
  SEARCH_URL = "http://www.google.com/search?q=%s&ie=utf8&oe=utf8&client=google-csbe&output=xml_no_dtd&cx=%s"
  
  @classmethod
  def GetQueryStringFuzzy(cls, query):
    query_string = []
    if query.filters:
      query_string.append(" ".join(["%s %s" % (key, value)
                                    for key, value in query.filters]))
    if query.terms:
      query_string.append(" ".join(query.terms))
      
    return " ".join(query_string)
  
  @classmethod
  def EscapeQueryString(cls, query_string):
    return urllib.quote_plus(query_string)
  
  @classmethod
  def GetSearchURL(cls, query, limit=None, offset=None):
    if isinstance(query, basestring):
      query_string = query
    else:
      query_string = cls.GetQueryStringFuzzy(query)

    escaped_query = cls.EscapeQueryString(query_string)
    
    url = cls.SEARCH_URL % (escaped_query, cls.SEARCH_ENGINE_ID)
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
    
    for result in xml_data.findall("RES/R"):
      course_url = result.find("U").text.strip()
      course_key = course_url.rsplit("/", 1)[1]
      results.latest_results.append(course_key)
      
    results.results.extend(results.latest_results)
  
  @classmethod
  def _ExtractSuggestion(cls, xml_data, results):
    suggestion_node = xml_data.find("Spelling/Suggestion")
    if suggestion_node is not None:
      results.suggested_query = suggestion_node.get("q")

  @classmethod
  def Search(cls, query, results, limit=None, offset=None, accuracy=None):
    # Compose the search URL    
    url = cls.GetSearchURL(query, limit, offset)
    logging.info("Performing GSS query at '%s'" % url)
    
    # Perform the query
    with contextlib.closing(urllib.urlopen(url)) as f:
      data = f.read()
      
      if f.getcode() != 200:
        logging.warning("Could not obtain search results from GSS")
        return

      xml_data = etree.ElementTree.fromstring(data)
      
    cls._ExtractCourseList(xml_data, results)
    cls._ExtractSuggestion(xml_data, results)


if __name__ == "__main__":
  unittest.main()