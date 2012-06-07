#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Populates a Google Site with the EPFL course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import contextlib
import getpass
import json
import logging
import urllib

from gdata.sites import client as gclient
from gdata.sites import data

MYEDU_URL = "http://7.courses-epfl.appspot.com"
SITEMAP_SUFFIX = "/admin/sitemap.json"


SITE_NAME = "myedu"
DOMAIN = "pocketcampus.org"

USER = "stefan.bucur@pocketcampus.org"


def ReadSitemap():
  url = "%s%s" % (MYEDU_URL, SITEMAP_SUFFIX)
  with contextlib.closing(urllib.urlopen(url)) as f:
    data = json.load(f, encoding="utf-8")
    
  return data


def ReadPageData(url):
  with contextlib.closing(urllib.urlopen(url)) as f:
    data = json.load(f, encoding="utf-8")
    
  return data

def _GetPagesFeed(client):
  uri = "%s?kind=webpage" % client.MakeContentFeedUri()
  feed = client.GetContentFeed(uri=uri)
  
  return feed    

def CleanupSite(client):
  feed = _GetPagesFeed(client)
  
  for entry in feed.entry:
    logging.info("Erasing page '%s'..." % entry.title.text)
    client.Delete(entry)


def PopulateSite(client):
  # Populate existing entries
  feed = _GetPagesFeed(client)
  existing_entries = {}
  for entry in feed.entry:
    logging.info("Found existing page %s" % entry.page_name.text)
    existing_entries[entry.page_name.text] = entry
  
  sitemap = ReadSitemap()
  
  for course_page_url in sitemap:
    logging.info("Processing %s..." % course_page_url)
    data = ReadPageData(course_page_url)
    
    if data["id"] in existing_entries:
      old_entry = existing_entries[data["id"]]
      old_entry.content.html = data["html"]
      entry = client.Update(old_entry)
      logging.info("Updated course page at %s" % entry.GetAlternateLink().href)
    else:
      entry = client.CreatePage('webpage', data["title"],
                                html=data["html"],
                                page_name=data["id"])
      logging.info("Created course page at %s" % entry.GetAlternateLink().href)
    
    


def Main():
  logging.basicConfig(level=logging.INFO)
  
  client = gclient.SitesClient(source="epfl-myedu-v10", site=SITE_NAME,
                               domain=DOMAIN)
  logging.info("Authenticating to Google Sites as %s..." % USER)
  password = getpass.getpass("Password:")
  client.ClientLogin(USER, password, client.source)
  
  PopulateSite(client)
  
  # entry = client.CreatePage('webpage', 'Test Page', html="<b>Hey there!</b>")
  # print "Created test page. View it at: %s" % entry.GetAlternateLink().href


if __name__ == "__main__":
  Main()