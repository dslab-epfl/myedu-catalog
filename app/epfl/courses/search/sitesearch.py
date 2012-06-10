#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Google Site Search provider."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import contextlib
import logging
import unittest
import urllib

import bs4
import unidecode


class SiteSearchProvider(object):
  SEARCH_ENGINE_ID = "000528554756935640955:t5p6oxkfane"
  SEARCH_URL = "http://www.google.com/search?q=%s&&client=google-csbe&output=xml_no_dtd&cx=%s"
  
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
    return urllib.quote_plus(unidecode.unidecode(query_string))
  
  @classmethod
  def GetSearchURL(cls, query, limit=None, offset=None):
    query_string = cls.GetQueryStringFuzzy(query)
    escaped_query = cls.EscapeQueryString(query_string)
    
    url = cls.SEARCH_URL % (escaped_query, cls.SEARCH_ENGINE_ID)
    if limit:
      url += "&num=%d" % limit
    if offset:
      url += "&start=%d" % offset
      
    return url

  @classmethod
  def Search(cls, query, limit=None, offset=None, accuracy=None, original=None):    
    url = cls.GetSearchURL(query, limit, offset)
    
    with contextlib.closing(urllib.urlopen(url)) as f:
      soup = bs4.BeautifulSoup(f.read())
      if f.getcode() != 200:
        logging.warning("Could not obtain search results from GSS")
        return
      
    logging.info(soup.prettify())

#    
#    xml_data = ElementTree.parse(StringIO.StringIO(u.content))
#    
#    course_list = []
#    
#    suggestion_node = xml_data.find("Spelling/Suggestion")
#    
#    if suggestion_node is not None and original is None:
#      logging.info("Searching instead for autosuggested %s" % suggestion_node.get("q"))
#      return cls.Search(parser.SearchQuery.ParseFromString(suggestion_node.get("q")),
#                        limit, offset, accuracy,
#                        xml_data.find("Q").text)
#    
#    number_found_node = xml_data.find("RES/M")
#    
#    if number_found_node is None:
#      logging.info("No search results found using query '%s'" % escaped_query)
#      return
#      
#    number_found = int(number_found_node.text)
#    
#    logging.info("%d search results found" % number_found)
#    
#    for result in xml_data.findall("RES/R"):
#      if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
#        for attr in result.findall("PageMap/DataObject/Attribute"):
#          if attr.get("name") == "title":
#            course_title = attr.text
#            course_key = models.Course.all().filter("title = ", course_title).get(keys_only=True)
#            if course_key:
#              course_list.append(course_key)
#      else:
#        course_url = result.find("U").text.strip()
#        url_tokens = course_url.split("/")
#        if url_tokens[-2] != "c":
#          continue
#        course_key = url_tokens[-1]
#        course_list.append(course_key)
#      
#    return SearchResults(course_list, number_found,
#                         xml_data.find("Q").text, original)

if __name__ == "__main__":
  unittest.main()