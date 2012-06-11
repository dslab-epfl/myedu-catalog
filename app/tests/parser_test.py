#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""Unit testing for query parser."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import unittest

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
    tokens = self.GetTokens("R�diger Andr� Gar�on")
    self.assertEqual(tokens, [("term", "R�diger"),
                              ("term", "Andr�"),
                              ("term", "Gar�on")])
    

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
    
    
class TestQueryGetString(unittest.TestCase):
  def test_simple_query(self):
    query = SearchQuery.ParseFromString(" help    me   out ")
    self.assertEqual(query.GetString(), "help me out")
    
  def test_filters_simple(self):
    query = SearchQuery.ParseFromString("looking for credits:10")
    self.assertEqual(query.GetString(), "credits:10 looking for")


if __name__ == "__main__":
  unittest.main()
