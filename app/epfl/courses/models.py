#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

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

class School(object):
  def __init__(self, code, title_en=None, title_fr=None):
    self.code = code
    self.title_en = title_en
    self.title_fr = title_fr
    
    self.sections = []
    
SCHOOLS = dict([(school.code, school) for school in [
  School("ENAC",
         title_en="Architecture, Civil, and Environmental Engineering"),
  School("IC",
         title_en="Computer and Communication Sciences"),
  School("SB", 
         title_en="Basic Sciences"),
  School("STI",
         title_en="Engineering",
         title_fr="Sciences et techniques de l'ingénieur"),
  School("SV",
         title_en="Life Sciences",
         title_fr="Sciences de la vie"),
  School("CDH",
         title_en="College of Humanities"),
  School("CDM",
         title_en="Management of Technology"),
  School("UNIL",
         title_en="University of Lausanne"),
  School("other",
         title_en="Other")
]])


class Section(object):
  def __init__(self, code, school, title_en=None, title_fr=None,
               minor=False, doctoral=False):
    self.code = code
    
    self.title_en = title_en
    self.title_fr = title_fr
    self.school = school
    self.minor = minor
    self.doctoral = doctoral
    
    SCHOOLS[school].sections.append(self)
    
SECTIONS = dict([(section.code, section) for section in [
  # ENAC
  Section('AR', 'ENAC',
          title_en='Architecture'),
  Section('AR_ECH', 'ENAC',
          title_en='Architecture Exchange'),
  Section('ENAC', 'ENAC',
          title_en='Architecture, Civil, and Environmental Engineering'),
  Section('GC', 'ENAC',
          title_en='Civil Engineering'),
  Section('MIN_DEV_TER', 'ENAC',
          title_en='Territorial Development minor'),
  Section('MIN_TEC_SPACE', 'ENAC',
          title_en='Space Technologies minor'),
  Section('SIE', 'ENAC',
          title_en='Environmental Sciences and Engineering'),
  
  # IC
  Section('EDIC', 'IC',
          title_en='Computer, Communication and Information Sciences',
          doctoral=True),
  Section('IN', 'IC',
          title_en='Computer Science'),
  Section('SC', 'IC',
          title_en='Communication Systems'),
  Section('SC_EPFL', 'IC',
          title_en='Communication Systems'),
  Section('MIN_BIOCOMP', 'IC',
          title_en='Biocomputing minor'),
  Section('MIN_IN_SEC', 'IC',
          title_en='Information Security', minor=True),
  
  # SB
  Section('CGC', 'SB',
          title_en='Chemistry and Chemical Engineering'),
  Section('CGC_CHIM', 'SB',
          title_en='Molecular and Biological Chemistry'),
  Section('CGC_ING', 'SB',
          title_en='Chemical Engineering and Biotechnology'),
  Section('ING_MATH', 'SB',
          title_en='Mathematics Engineering'),
  Section('ING_PHYS', 'SB',
          title_en='Physics Engineering'),
  Section('MA', 'SB',
          title_en='Mathematics'),
  Section('MATH', 'SB',
          title_en='Mathematics'),
  Section('MA_CO', 'SB',
          title_en='Computational Science and Engineering'),
  Section('MIN_BIOMED', 'SB',
          title_en='Biomedical Technologies', minor=True),
  Section('MIN_ENER', 'SB',
          title_en='Energy', minor=True),
  Section('PH', 'SB',
          title_en='Physics'),
  Section('PHYS', 'SB',
          title_en='Physics'),
  Section('PH_NE', 'SB',
          title_en='Nuclear engineering'),
 
  # STI
  Section('EL', 'STI',
          title_en='Electrical and Electronics Engineering'),
  Section('EME_MES', 'EL',
          title_en='Energy Management and Sustainability'),
  Section('GM', 'STI',
          title_en='Mechanical Engineering'),
  Section('MNIS', 'STI',
          title_en='Micro and Nanotechnologies for Integrated Systems'),
  Section('MT', 'STI',
          title_en='Microengineering'),
  Section('MX', 'STI',
          title_en='Materials Science and Engineering'),
  
  # SV
  Section('EDNE', 'SV',
          title_en='Neuroscience', doctoral=True),
  Section('MIN_BIOTECH', 'SV',
          title_en='Biotechnology', minor=True),
  Section('SV', 'SV',
          title_en='Life Sciences and Technologies'),
  Section('SV_B', 'SV',
          title_en='Bioengineering'),
  Section('SV_STV', 'SV',
          title_en='Life Sciences and Technologies'),
  
  # CDH
  Section('MIN_AREA_CULTURAL', 'CDH',
          title_en='Area and Cultural Studies', minor=True),
  Section('SHS', 'CDH',
          title_en='Humanities and Social Sciences'),
  
  # CDM  
  Section('EDMT', 'CDM',
          title_en='Management of Technology', doctoral=True),
  Section('IF', 'CDM',
          title_en='Financial Engineering'),
  Section('MIN_MTE', 'CDM',
          title_en='Management of Technology and Entrepreneurship', minor=True),
  Section('MTE', 'CDM',
          title_en='Management of Technology'),
 
  # UNIL
  Section('UNIL_BIU', 'UNIL',
          title_fr='UNIL - Biologie'),
  Section('UNIL_CSU', 'UNIL',
          title_fr='UNIL - Collège des sciences'),
  Section('UNIL_GEU', 'UNIL',
          title_fr='UNIL - Géosciences'),
  Section('UNIL_HEC', 'UNIL',
          title_fr='UNIL - Hautes études commerciales'),
  Section('UNIL_MEU', 'UNIL',
          title_fr='UNIL - Médicine'),
  Section('UNIL_PHU', 'UNIL',
          title_fr='UNIL - Pharmacie'),
  Section('UNIL_SFU', 'UNIL',
          title_fr='UNIL - Sciences forensiques'),
 
  # Other
  Section('HPLANS', 'other',
          title_fr='Hors Plans'),
]])


class StudyPlan(object):
  PLANS = {
    "BA": "Bachelor",
    "MA": "Master",
    "PM": "Master project",
  }
  
  SEMESTERS = {
    "E": "Spring",
    "H": "Fall",
    "1": "1st semester",
    "2": "2nd semester",
    "3": "3rd semester",
    "4": "4th semester",
    "5": "5th semester",
    "6": "6th semester"
  }
  
  def __init__(self, code):
    self.code = code
    parts = self.code.split("-")
    
    self.section = Section(parts[0])
    self._plan = None
    self._semester = None
    
    if len(parts) < 2:
      return
    
    if len(parts[1]) == 3:
      self._plan = parts[1][0:2]
      self._semester = parts[1][2]
    elif len(parts[1]) == 1:
      self._semester = parts[1]
    else:
      raise ValueError("Invalid plan syntax")

  @property
  def plan_code(self):
    return self._plan
  
  @property
  def semester_code(self):
    return self._semester
  
  @property
  def plan(self):
    return self.PLANS.get(self._plan)
  
  @property
  def semester(self):
    return self.SEMESTERS.get(self._semester)
    

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
  client_address = db.StringProperty()
