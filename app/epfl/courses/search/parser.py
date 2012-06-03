#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Query parser."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import re
import unittest


TOKEN_PATTERN = r"""
(?P<term>[^\s"':]+)
|(?P<doublequote>\".*?(?:"|$))
|(?P<singlequote>\'.*?(?:'|$))
|(?P<whitespace>[\s]+)
|(?P<colon>[:])
"""

TOKEN_RE = re.compile(TOKEN_PATTERN, re.VERBOSE | re.UNICODE)

def TokenizeQuery(query_string, discard_ws=True):
  position = 0
  while True:
    m = TOKEN_RE.match(query_string, position)
    if not m:
      break
    position = m.end()
    token_name = m.lastgroup
    token_value = m.group(token_name)
    if discard_ws and token_name == "whitespace":
      continue
    yield token_name, token_value
  if position != len(query_string):
    raise ValueError("Tokenization error at position %d of %d"
                     % (position, len(query_string)))
    
    
class SearchQuery(object):
  def __init__(self, terms=None, filters=None, directives=None):
    self.terms = terms or []
    self.filters = filters or []
    self.directives = directives or {}
    
  def GetString(self, include_directives=True):
    query_string = []
    if self.directives and include_directives:
      query_string.append(" ".join(["@%s:%s" % (key, value)
                                    for key, value in self.directives.items()]))
    if self.filters:
      query_string.append(" ".join(["%s:%s" % (key, value)
                                    for key, value in self.filters]))
      
    if self.terms:
      query_string.append(" ".join(self.terms))
      
    return " ".join(query_string)
    
  @classmethod
  def ParseFromString(cls, query_string):
    query = cls()
    
    last_term = None
    found_colon = False
    is_directive = False
    
    for tname, tvalue in TokenizeQuery(query_string):
      if tname == "doublequote" or tname == "singlequote" or tname == "term":
        if found_colon:
          if is_directive:
            query.directives[last_term.lstrip("@")] = tvalue
          else:
            query.filters.append((last_term, tvalue))
          query.terms.pop()

          found_colon = False
          last_term = None
          is_directive = False
        else:
          is_directive = tvalue.startswith("@")
          last_term = tvalue
          query.terms.append(tvalue)
      elif tname == "colon":
        if last_term:
          found_colon = True
        else:
          found_colon = False
          query.terms.append(tvalue)
          
    return query
      
  @classmethod
  def BuildFromRequest(cls, request):
    def append_filter(query, id_name, field_name):
      field_value = request.get(id_name)
      if field_value:
        query.filters.append((field_name, field_value))
      
    query = cls.ParseFromString(request.get("q", ""))
    
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
    
    
class TestQueryGetString(unittest.TestCase):
  def test_simple_query(self):
    query = SearchQuery.ParseFromString(" help    me   out ")
    self.assertEqual(query.GetString(), "help me out")
    
  def test_filters_simple(self):
    query = SearchQuery.ParseFromString("looking for credits:10")
    self.assertEqual(query.GetString(), "credits:10 looking for")

if __name__ == "__main__":
  unittest.main()
