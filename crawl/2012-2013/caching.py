#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Caching utilities."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import logging


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
