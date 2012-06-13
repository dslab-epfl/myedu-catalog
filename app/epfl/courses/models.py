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
  note = db.TextProperty()
  prerequisite_for = db.TextProperty()
  library_recomm = db.TextProperty()
  links = db.TextProperty()

  needs_indexing_ = db.BooleanProperty(default=True)
  
  @classmethod
  def TotalCount(cls):
    stat = stats.KindStat.all().filter("kind_name =", cls.__name__).get()
    return stat.count
    

class SearchQueryRecord(db.Model):
  q = db.TextProperty()
  aq_t = db.TextProperty()
  aq_lang = db.TextProperty()
  aq_in = db.TextProperty()
  aq_sec = db.TextProperty()
  aq_sem = db.TextProperty()
  aq_exam = db.TextProperty()
  aq_cred = db.TextProperty()
  aq_coeff = db.TextProperty()
  
  aq_hours_l = db.TextProperty()
  aq_hours_r = db.TextProperty()
  aq_hours_p = db.TextProperty()
  
  translated_query = db.TextProperty()
  suggested_query = db.TextProperty()
  
  results_count = db.IntegerProperty()
  offset = db.IntegerProperty()
  
  time_stamp = db.DateTimeProperty(auto_now_add=True)
