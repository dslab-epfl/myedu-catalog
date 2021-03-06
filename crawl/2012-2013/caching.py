#!/usr/bin/env python
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

"""Caching utilities."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import contextlib
import json
import logging
import os
import urllib
import urlparse


this_dir = os.path.dirname(__file__)


def CachedJSON(file_name):
  """Decorator factory that caches the result of a function in a JSON file."""

  def decorator(func):
    def wrapper(*args, **kwargs):
      try:
        with open(file_name, "r") as f:
          data = json.load(f, encoding="utf-8")
        logging.info("Found cached data at '%s'" % file_name)
        return data
      except IOError:
        pass

      logging.info("Data not found at '%s'. Computing." % file_name)
      data = func(*args, **kwargs)

      try:
        with open(file_name, "w") as f:
          json.dump(data, f, indent=True, encoding="utf-8")
        logging.info("Saved computed data at '%s'" % file_name)
      except IOError:
        logging.info("Could not save computed data at '%s'" % file_name)

      return data

    return wrapper
  return decorator


def CachedURLGet(url):
  """Read and cache the contents of a URL."""

  # Construct the file name of the cache
  parsed_url = urlparse.urlsplit(url)
  parsed_url_path = parsed_url.path.lstrip("/")
  if parsed_url.query:
    parsed_url_path += "?" + parsed_url.query

  cache_file_name = os.path.join(this_dir, parsed_url.netloc, parsed_url_path)

  try:
    with open(cache_file_name, "r") as f:
      data = f.read()
    logging.info("URL cache found for %s [%s]" % (url, cache_file_name))
    return data
  except IOError:
    pass

  logging.info("URL not cached. Retrieving %s" % url)

  with contextlib.closing(urllib.urlopen(url)) as f:
    data = f.read()

  try:
    try:
      os.makedirs(os.path.dirname(cache_file_name))
    except OSError:
      pass

    with open(cache_file_name, "w") as f:
      f.write(data)
    logging.info("Saved URL data for %s [%s]" % (url, cache_file_name))
  except IOError:
    logging.info("Could not save cache for URL %s at %s" % (url, cache_file_name))

  return data
