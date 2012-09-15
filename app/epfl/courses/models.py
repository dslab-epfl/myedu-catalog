#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""Data models for our application."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


from google.appengine.ext import db
from google.appengine.ext.db import stats


class School(db.Model):
  OTHER = "other"
  
  title_en = db.StringProperty()
  title_fr = db.StringProperty()
  
  def title(self, use_french=False):
    if use_french:
      return self.title_fr or self.title_en
    else:
      return self.title_en or self.title_fr
    
  @property
  def code(self):
    return self.key().name()


class Section(db.Model):
  title_short = db.StringProperty()
  title_en = db.StringProperty()
  title_fr = db.StringProperty()
  
  school = db.ReferenceProperty(School)
  
  minor = db.BooleanProperty(default=False)
  master = db.BooleanProperty(default=False)
  
  alias = db.StringProperty()
  
  def title(self, use_french=False):
    if use_french:
      return self.title_fr or self.title_en
    else:
      return self.title_en or self.title_fr
    
  def display_name(self, use_french=False, short=False):
    if short:
      name = self.title_short or self.code
    else:
      name = self.title(use_french)

    if self.minor:
      name += " (minor)" if not use_french else " (mineur)"
    elif self.master:
      name += " (master)"
      
    return name
    
  @property
  def code(self):
    return self.key().name()


class Course(db.Model):
  desc_language_ = db.StringProperty(choices=set(["en", "fr"]))
  
  title = db.StringProperty()
  
  language = db.StringProperty()
  
  section_keys = db.ListProperty(db.Key)
  study_plans = db.StringListProperty()
  code_prefix = db.StringListProperty()
  code_number = db.StringListProperty()
  
  instructors = db.StringListProperty()
  urls = db.StringListProperty()
  
  credit_count = db.IntegerProperty()
  coefficient = db.FloatProperty()
  
  semester = db.StringProperty()
  exam_form = db.StringProperty()
  
  lecture_time = db.IntegerProperty(default=0)
  lecture_weeks = db.IntegerProperty(default=0)
  
  recitation_time = db.IntegerProperty(default=0)
  recitation_weeks = db.IntegerProperty(default=0)
  
  # This includes lab and practical hours
  project_time = db.IntegerProperty(default=0)
  project_weeks = db.IntegerProperty(default=0)
  
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
  links = db.StringListProperty()

  needs_indexing_ = db.BooleanProperty(default=True)
  
  @classmethod
  def TotalCount(cls):
    stat = stats.KindStat.all().filter("kind_name =", cls.__name__).get()
    return stat.count
  
  @property
  def sections(self):
    return Section.get(self.section_keys)
  
  @property
  def course_id(self):
    return self.key().name()[3:]
  
  @property
  def codes(self):
    pass
  
  @classmethod
  def GetByCourseID(cls, course_id, lang="en"):
    if isinstance(course_id, basestring):
      return cls.get_by_key_name("%s:%s" % (lang, course_id))
    else:
      return cls.get_by_key_name(["%s:%s" % (lang, cid) for cid in course_id])
  

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
  client_address = db.StringProperty()
