#!/usr/bin/env python

"""Data models for our application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


from google.appengine.ext import db


LANGUAGE_MAPPING = {
  "en": "English",
  "fr": "French"
}

SPECIALIZATION_MAPPING = {
  "IN": "Computer Science",
  "SC": "Communication Sciences",
  "SV": "Life Sciences"
}

INDEX_NAME = 'courses-index'


class Course(db.Model):
  title = db.StringProperty()
  language = db.StringProperty(choices=set(["en", "fr", "de", "fr_en"]))
  
  instructors = db.StringListProperty()
  sections = db.StringListProperty()
  study_plans = db.StringListProperty()
  urls = db.StringListProperty()
