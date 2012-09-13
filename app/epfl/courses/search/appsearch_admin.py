#!/usr/bin/env python

"""Functionality to support search."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import itertools
import logging
import unicodedata

from google.appengine.api import search
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from epfl.courses import base_handler
from epfl.courses import config
from epfl.courses import models


class AppEngineIndex(object):
  INDEX_NAME = 'courses-index'
  
  LANGUAGE_INDEX = {
    "en": "courses-index-en",
    "fr": "courses-index-fr",
  }
  
  class FieldMapper(object):
    """Convenience class for constructing a search document field."""
    
    def __init__(self, orig_value, search_field, field_name, xform=None,
                 multi=False, language=None):
      self.orig_value = orig_value
      self.search_field = search_field
      self.field_name = field_name
      self.xform = xform
      self.multi = multi
      self.language = language
      
    def ConstructFields(self):
      if not self.orig_value:
        return
      
      if not self.multi:
        values = [self.orig_value]
      else:
        values = self.orig_value
        
      values = [(self.xform(v) if self.xform else v) for v in values]
        
      if self.search_field != search.NumberField:
        values = [unicodedata.normalize('NFKD', unicode(v)).encode("ascii", "ignore")
                  for v in values]
      
      return [self.search_field(name=self.field_name, value=v) for v in values]
      
  @classmethod
  def GetIndex(cls, language=None):
    """Obtain the search index where the courses are indexed."""
    
    if not language:
      return search.Index(name=cls.INDEX_NAME)
    else:
      return search.Index(name=cls.LANGUAGE_INDEX[language])
      
  @classmethod
  def ClearCourseIndex(cls):
    """Remove all course information in the search index."""
    
    for docindex in [cls.GetIndex(), cls.GetIndex("en"), cls.GetIndex("fr")]:
      while True:
        document_ids = [document.doc_id
                        for document in docindex.list_documents(ids_only=True)]
        if not document_ids:
          break
        docindex.remove(document_ids)
        logging.info('Removed %d documents.' % len(document_ids))
      
  @classmethod
  def ClearIndexingStatus(cls, courses):
    for course in courses:
      course.needs_indexing_ = True
    db.put(courses)
    
  @classmethod
  def _GetDocumentFields(cls, course, language=None):
    """Return language agnostic fields if language is None, otherwise return
    language-specific fields."""
    
    if not language:
      # Language-agnostic fields
      mappings = [
        cls.FieldMapper(course.language, search.AtomField, 'language'),
        cls.FieldMapper(course.instructors, search.TextField, 'instructor',
                        multi=True),
        # The section codes
        cls.FieldMapper(course.sections, search.AtomField, 'section',
                        lambda s: s.code, multi=True),
        # The study plan codes
        cls.FieldMapper(course.study_plans, search.TextField, 'plan',
                        multi=True),
        cls.FieldMapper(course.credit_count, search.NumberField, 'credits'),
        cls.FieldMapper(course.coefficient, search.NumberField, 'coefficient'),
        cls.FieldMapper(course.lecture_time, search.NumberField, 'lecthours'),
        cls.FieldMapper(course.recitation_time, search.NumberField, 'recithours'),
        cls.FieldMapper(course.project_time, search.NumberField, 'projhours'),
        cls.FieldMapper(course.links, search.HtmlField, 'links',
                  multi=True),
      ]
    else:
      # Language-specific fields
      mappings = [
        cls.FieldMapper(course.title, search.TextField, 'title',
                        language=language),
        # Human-readable section title
        cls.FieldMapper(course.sections, search.TextField, 'section',
                        lambda s: s.title(use_french=(language == "fr")),
                        multi=True, language=language),
        # Human-readable study plan
        cls.FieldMapper(course.study_plans, search.TextField, 'plan',
                        lambda p: config.STUDY_PLANS[language][p], multi=True,
                        language=language),
        cls.FieldMapper(course.semester, search.AtomField, 'semester',
                        language=language),
        cls.FieldMapper(course.exam_form, search.AtomField, 'exam',
                        language=language),
  
        # TODO(bucur): Maybe consolidate these in one field?
        cls.FieldMapper(course.learning_outcomes, search.HtmlField, 'outcomes',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.content, search.HtmlField, 'content',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.prior_knowledge, search.HtmlField, 'prereq',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.type_of_teaching, search.HtmlField, 'teaching',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.bibliography, search.HtmlField, 'biblio',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.keywords, search.HtmlField, 'keywords',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.exam_form_detail, search.HtmlField, 'examdetail',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.note, search.HtmlField, 'note',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.prerequisite_for, search.HtmlField, 'prereqfor',
                        lambda value: base_handler.BaseHandler.ISAMarkup(value),
                        language=language),
        cls.FieldMapper(course.library_recomm, search.HtmlField, 'libraryrec',
                        language=language),
      ]
      
    doc_fields = []
    for mapper in mappings:
      fields = mapper.ConstructFields()
      if fields:
        doc_fields.extend(fields)
        
    return doc_fields
  
  @classmethod
  def _CreateDocumentForCourse(cls, course_en, course_fr):
    doc_fields = []
    primary_course = course_en or course_fr
    
    doc_fields.extend(cls._GetDocumentFields(primary_course))
    if course_en:
      doc_fields.extend(cls._GetDocumentFields(course_en, language="en"))
    if course_fr:
      doc_fields.extend(cls._GetDocumentFields(course_fr, language="fr"))
    
    return search.Document(doc_id=primary_course.course_id,
                           fields=doc_fields)
  
  @classmethod  
  def _IndexDocuments(cls, doc_bag, language_index=False):
    """Atomically index a bag of documents and update their indexing status."""
    
    docs, courses = zip(*doc_bag)
    
    docs_all, docs_en, docs_fr = zip(*docs)
    courses_en, courses_fr = zip(*courses)
    
    try:
      cls.GetIndex().add(docs_all)
      if language_index:
        cls.GetIndex(language="en").add(docs_en)
        cls.GetIndex(language="fr").add(docs_fr)
    except apiproxy_errors.OverQuotaError:
      logging.error("Over quota error.")
      return False
    else:
      db.put(courses_en + courses_fr)
      logging.info('Added %d documents to the index.' % len(doc_bag))
      return True

  @classmethod
  def UpdateCourseIndex(cls, language_index=False):
    """Update the search index for the given courses."""
    
    queries = {}
    
    for language in ["en", "fr"]:
      q = models.Course.all().filter("needs_indexing_ =", True)
      q.filter("desc_language_ =", language)
      q.order("__key__")
      queries[language] = q.fetch(limit=None)
    
    BATCH_SIZE = 50
    doc_bag = []
    
    for course_en, course_fr in itertools.izip(queries["en"], queries["fr"]):
      # Make sure they refer to same course
      assert course_en.course_id == course_fr.course_id
      
      doc_all = cls._CreateDocumentForCourse(course_en, course_fr)
      doc_en = cls._CreateDocumentForCourse(course_en, None)
      doc_fr = cls._CreateDocumentForCourse(None, course_fr)
      
      course_en.needs_indexing_ = False
      course_fr.needs_indexing_ = False
      
      doc_bag_item = ((doc_all, doc_en, doc_fr), (course_en, course_fr))
      
      if len(doc_bag) == BATCH_SIZE:
        if not cls._IndexDocuments(doc_bag, language_index):
          return False
        doc_bag = [doc_bag_item]
      else:
        doc_bag.append(doc_bag_item)
    if doc_bag:
      if not cls._IndexDocuments(doc_bag, language_index):
        return False
      
    return True

  