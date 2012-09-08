#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

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
