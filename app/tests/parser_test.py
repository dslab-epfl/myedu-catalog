#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""Unit testing for query parser."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import sys
import unittest

sdk_path = "/usr/local/google_appengine"
sys.path.insert(0, sdk_path)
import dev_appserver
dev_appserver.fix_sys_path()

from epfl.courses.search.parser import TokenizeQuery
from epfl.courses.search.parser import SearchQuery


class TestTokenizeQuery(unittest.TestCase):
  @classmethod
  def GetTokens(cls, query_string, **kwargs):
    return [token for token in TokenizeQuery(query_string, **kwargs)]
  
  def test_simple_query(self):
    tokens = self.GetTokens("help me out")
    self.assertEqual(tokens, [("term", "help"), ("term", "me"),
                              ("term", "out")])
    
  def test_empty(self):
    tokens = self.GetTokens("")
    self.assertEqual(tokens, [])
    
  def test_whitespace(self):
    tokens = self.GetTokens("search  that", discard_ws=False)
    self.assertEqual(tokens, [("term", "search"),
                              ("whitespace", "  "),
                              ("term", "that")])
    
  def test_quotes(self):
    tokens = self.GetTokens('search "something else"')
    self.assertEqual(tokens, [("term", "search"),
                              ("doublequote", '"something else"')])
    
  def test_unfinished_quotes(self):
    tokens = self.GetTokens('search "something else')
    self.assertEqual(tokens, [("term", "search"),
                              ("doublequote", '"something else')])
    
  def test_filter_simple(self):
    tokens = self.GetTokens('instructor: candea')
    self.assertEqual(tokens, [("term", "instructor"),
                              ("colon", ":"),
                              ("term", "candea")])
    
  def test_filter_complex(self):
    tokens = self.GetTokens('instructor:"George Candea"')
    self.assertEqual(tokens, [("term", "instructor"),
                              ("colon", ":"),
                              ("doublequote", '"George Candea"')])
    
  def test_unicode(self):
    tokens = self.GetTokens("Rüdiger André Garçon")
    self.assertEqual(tokens, [("term", "Rüdiger"),
                              ("term", "André"),
                              ("term", "Garçon")])
    

class TestParseQuery(unittest.TestCase):
  def test_simple_query(self):
    query = SearchQuery.ParseFromString("help me out")
    self.assertEqual(query.terms, ["help", "me", "out"])
    
  def test_empty(self):
    query = SearchQuery.ParseFromString("")
    self.assertEqual(query.terms, [])
    self.assertEqual(query.filters, [])
    self.assertEqual(query.directives, {})
    
  def test_filters_simple(self):
    query = SearchQuery.ParseFromString("help a:b c: d")
    self.assertEqual(query.terms, ["help"])
    self.assertEqual(query.filters, [("a", "b"), ("c", "d")])
    
  def test_filters_chained_colon(self):
    query = SearchQuery.ParseFromString("a:b:c")
    self.assertEqual(query.terms, [":", "c"])
    self.assertEqual(query.filters, [("a", "b")])
    
  def test_directive(self):
    query = SearchQuery.ParseFromString("@loc:db query")
    self.assertEqual(query.terms, ["query"])
    self.assertEqual(query.directives, { "loc": "db" })
    
  def test_complex_query(self):
    query = SearchQuery.ParseFromString('instructor:"le boudec" or instructor:hubaux')
    self.assertEqual(query.terms, ["OR"])
    self.assertEqual(query.filters, [("instructor", '"le boudec"'), ("instructor", "hubaux")])
    self.assertEqual(query.directives, {})
    
    
class TestQueryGetString(unittest.TestCase):
  def test_simple_query(self):
    query = SearchQuery.ParseFromString(" help    me   out ")
    self.assertEqual(query.GetString(), "help me out")
    
  def test_filters_simple(self):
    query = SearchQuery.ParseFromString("looking for credits:10")
    self.assertEqual(query.GetString(), "looking for credits:10")
    
  def test_complex_query(self):
    query = SearchQuery.ParseFromString('instructor:"le boudec" or instructor:hubaux')
    self.assertEqual(query.GetString(), 'instructor:"le boudec" OR instructor:hubaux')
    

class TestReplaceFilter(unittest.TestCase):
  def test_complex_query(self):
    query = SearchQuery.ParseFromString('instructor:"le boudec" or instructor:hubaux')
    query.ReplaceFilter("instructor", "candea")
    
    self.assertEqual(query.terms, ["OR"])
    self.assertEqual(query.filters, [("instructor", "candea")])
    self.assertEqual(query.GetString(), 'OR instructor:candea')
    

class TestExtractTerms(unittest.TestCase):
  def test_simple_query(self):
    query = SearchQuery.ParseFromString('test')
    self.assertEqual(query.ExtractTerms(), ['test'])


if __name__ == "__main__":
  unittest.main()
