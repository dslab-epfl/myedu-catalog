#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
  TERM = 0
  FILTER = 1
  DIRECTIVE = 2

  def __init__(self, terms=None, filters=None, directives=None):    
    self.components = []
    if directives:
      self.components.extend([(self.DIRECTIVE, (k, v)) for k, v in directives.iteritems()])
    if filters:
      self.components.extend([(self.FILTER, (k, v)) for k, v in filters])
    if terms:
      self.components.extend([(self.TERM, term) for term in terms])
    
  @property
  def terms(self):
    return [term for t, term in self.components if t == self.TERM]
  
  @property
  def filters(self):
    return [filt for t, filt in self.components if t == self.FILTER]
  
  @property
  def directives(self):
    return dict([directive for t, directive in self.components
                 if t == self.DIRECTIVE])

  def ReplaceFilter(self, key, value):
    self.components[:] = [(t, v) for t, v in self.components
                          if t != self.FILTER or v[0] != key]
    self.components.append((self.FILTER, (key, value)))
    
  def GetString(self, include_directives=True):
    query_string = []
    
    for t, value in self.components:
      if t == self.DIRECTIVE and include_directives:
        query_string.append("@s:%s" % (value[0], value[1]))
        
      if t == self.FILTER:
        query_string.append("%s:%s" % (value[0], value[1]))
        
      if t == self.TERM:
        query_string.append(value)
      
    return " ".join(query_string)
  
  def ExtractTerms(self):
    result = []
    
    for t, value in self.components:
      if t == self.FILTER:
        result.extend(re.findall(r"\w+", value[1], re.UNICODE))
        
      if t == self.TERM:
        result.extend(re.findall(r"\w+", value, re.UNICODE))
      
    return result
  
  @classmethod
  def _FixSpecialTerm(cls, term):
    lo_term = term.lower()
    if lo_term == "or":
      return "OR"
    
    return term
    
  @classmethod
  def ParseFromString(cls, query_string):
    query = cls()
    
    last_term = None
    found_colon = False
    is_directive = False
    
    for tname, tvalue in TokenizeQuery(query_string):
      if tname == "doublequote" or tname == "singlequote" or tname == "term":
        if found_colon:
          query.components.pop()
          if is_directive:
            query.components.append((cls.DIRECTIVE, (last_term.lstrip("@"), tvalue)))
          else:
            query.components.append((cls.FILTER, (last_term, tvalue)))

          found_colon = False
          last_term = None
          is_directive = False
        else:
          is_directive = tvalue.startswith("@")
          last_term = tvalue
          query.components.append((cls.TERM, cls._FixSpecialTerm(tvalue)))
      elif tname == "colon":
        if last_term:
          found_colon = True
        else:
          found_colon = False
          query.components.append((cls.TERM, cls._FixSpecialTerm(tvalue)))
          
    return query

