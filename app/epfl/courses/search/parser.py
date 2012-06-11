#!/usr/bin/env python

"""Query parser."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import re


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
