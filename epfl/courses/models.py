#!/usr/bin/env python

"""Data models for our application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


from google.appengine.ext import db
from google.appengine.ext.db import stats


LANGUAGE_MAPPING = {
  "en": "English",
  "fr": "French",
  "de": "German",
  "fr_en": "French and English"
}

SPECIALIZATION_MAPPING = {
  "IN": "Computer Science",
  "SC": "Communication Sciences",
  "SV": "Life Sciences"
}


class Course(db.Model):
  title = db.StringProperty()
  language = db.StringProperty(choices=set(["en", "fr", "de", "fr_en"]))
  
  instructors = db.StringListProperty()
  sections = db.StringListProperty()
  study_plans = db.StringListProperty()
  urls = db.StringListProperty()
  
  credit_count = db.IntegerProperty()
  coefficient = db.FloatProperty()
  
  semester = db.StringProperty(choices=set(["Fall", "Spring"]))
  exam_form = db.StringProperty()
  
  lecture_time = db.IntegerProperty(default=0)
  lecture_weeks = db.IntegerProperty(default=0)
  
  recitation_time = db.IntegerProperty(default=0)
  recitation_weeks = db.IntegerProperty(default=0)
  
  project_time = db.IntegerProperty(default=0)
  project_weeks = db.IntegerProperty(default=0)
  
  practical_time = db.IntegerProperty(default=0)
  practical_weeks = db.IntegerProperty(default=0)
  
  learning_outcomes = db.TextProperty()
  content = db.TextProperty()
  prior_knowledge = db.TextProperty()
  type_of_teaching = db.TextProperty()
  bibliography = db.TextProperty()
  keywords = db.TextProperty()
  exam_form_detail = db.TextProperty()

  needs_indexing_ = db.BooleanProperty(default=True)
  
  @classmethod
  def TotalCount(cls):
    stat = stats.KindStat.all().filter("kind_name =", cls.__name__).get()
    return stat.count
    