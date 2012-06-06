#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Populates a Google Site with the EPFL course catalog."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import getpass
import logging

from gdata.sites import client as gclient
from gdata.sites import data


SITE_NAME = "myedu"
DOMAIN = "pocketcampus.org"

USER = "stefan.bucur@pocketcampus.org"


def Main():
  logging.basicConfig(level=logging.INFO)
  
  client = gclient.SitesClient(source="epfl-myedu-v10", site=SITE_NAME,
                               domain=DOMAIN)
  logging.info("Authenticating to Google Sites as %s..." % USER)
  password = getpass.getpass("Password:")
  client.ClientLogin(USER, password,
                     client.source)
  
  client.site = SITE_NAME
  
  entry = client.CreatePage('webpage', 'Test Page', html="<b>Hey there!</b>")
  print "Created test page. View it at: %s" % entry.GetAlternateLink().href


if __name__ == "__main__":
  Main()