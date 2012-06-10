#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Performs a GSite search by scraping Google Sites search results."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import contextlib
import re
import urllib

import bs4


class GoogleSitesSearch(object):
  SEARCH_URL = "https://sites.google.com/a/pocketcampus.org/myedu/system/app/pages/search?scope=search-site&q=%s&offset=%d"
  SEARCH_HDR = re.compile(r"Showing (\d+)-(\d+) of (\d+) results")
  
  def __init__(self, query_text):
    self.query_text = query_text
    self.results = []
    self.last_results = []
    
    self._total = None
    self._offset = 0
    
  @property
  def total(self):
    return self._total
  
  @property
  def offset(self):
    return self._offset
    
  def FetchResults(self):
    with contextlib.closing(urllib.urlopen(self.SEARCH_URL % (self.query_text, self._offset))) as f:
      soup = bs4.BeautifulSoup(f.read())
      
    try:
      header = soup.find(attrs={ "id": "sites-showing-results" }).p.text
      match = self.SEARCH_HDR.match(header)
      self._total = int(match.group(3))
    finally:
      pass
    
    self.last_results = []
  
    for result in soup.find_all(attrs={ "class": "sites-search-result"}):
      self.last_results.append(result.h3.a["href"].rsplit("/", 1)[1])
      
    self.results.extend(self.last_results)
    self._offset += len(self.last_results)


def Main():
  gss = GoogleSitesSearch("test")
  
  while True:
    gss.FetchResults()
    if not gss.last_results:
      break
    
    print gss.last_results


if __name__ == "__main__":
  Main()