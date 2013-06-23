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

"""AppEngine search."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging
import unicodedata

from google.appengine.api import search
from google.appengine.runtime import apiproxy_errors


class AppSearchProvider(object):
  INDEX_NAME = 'courses-index'
  
  MAX_SORT_LIMIT = 500
  
  @classmethod
  def GetIndex(cls):
    return search.Index(name=cls.INDEX_NAME)
  
  @classmethod
  def GetQueryString(cls, query):
    return unicodedata.normalize('NFKD', query.GetString(include_directives=False)).encode("ascii", "ignore")
  
  @classmethod
  def Search(cls, query, results, limit=None, offset=None, accuracy=None):
    if isinstance(query, basestring):
      query_string = query
    else:
      query_string = cls.GetQueryString(query)
      
    results.latest_results = []
    
    try:
      sort_expr = [
        search.SortExpression("_score",
                              direction=search.SortExpression.DESCENDING,
                              default_value=0.0),
        search.SortExpression("title",
                              direction=search.SortExpression.ASCENDING,
                              default_value="")
      ]
      sort_opts = search.SortOptions(sort_expr,
                                     match_scorer=search.MatchScorer(),
                                     limit=cls.MAX_SORT_LIMIT)
      
      search_query = search.Query(query_string,
                                  search.QueryOptions(limit=limit,
                                                      offset=offset,
                                                      sort_options=sort_opts,
                                                      number_found_accuracy=accuracy,
                                                      ids_only=True))
      search_results = cls.GetIndex().search(search_query)
      
      results.number_found = search_results.number_found
      results.latest_results = [document.doc_id for document in search_results.results]
      results.results.extend(results.latest_results)
    except apiproxy_errors.OverQuotaError:
      logging.error("Over quota error")
    except ValueError:
      logging.error("Invalid values")
    except Exception:
      logging.exception("Unknown search error")
