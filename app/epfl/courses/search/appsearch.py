#!/usr/bin/env python

"""Functionality to support search."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import logging

from google.appengine.api import search
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from epfl.courses import models

import unidecode

class AppEngineIndex(object):
  INDEX_NAME = 'courses-index'
  
  class FieldMapper(object):
    def __init__(self, orig_value, search_field, field_name, xform=None):
      self.orig_value = orig_value
      self.search_field = search_field
      self.field_name = field_name
      self.xform = xform
      
    def ConstructField(self):
      if not self.orig_value:
        return
      
      if self.xform:
        value = self.xform(self.orig_value)
      else:
        value = self.orig_value
        
      if self.search_field != search.NumberField:
        value = unidecode.unidecode(value)
      
      return self.search_field(name=self.field_name,
                               value=value)
      
  @classmethod
  def GetIndex(cls):
    """Obtain the search index where the courses are indexed."""
    
    return search.Index(name=cls.INDEX_NAME)
      
  @classmethod
  def ClearCourseIndex(cls):
    """Remove all course information in the search index."""
    
    docindex = cls.GetIndex()
    
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
  def _CreateDocumentForCourse(cls, course):
    mappings = [
      cls.FieldMapper(course.title, search.TextField, 'title'),
      cls.FieldMapper(course.language, search.TextField, 'language',
                      lambda value: models.LANGUAGE_MAPPING[value]),
      cls.FieldMapper(course.instructors, search.TextField, 'instructor',
                      lambda value: ", ".join(value)),
      cls.FieldMapper(course.sections, search.TextField, 'section',
                      lambda value: ", ".join(value)),
      cls.FieldMapper(course.study_plans, search.TextField, 'plan',
                      lambda value: ", ".join(value)),
      cls.FieldMapper(course.credit_count, search.NumberField, 'credits'),
      cls.FieldMapper(course.coefficient, search.NumberField, 'coefficient'),
      cls.FieldMapper(course.semester, search.AtomField, 'semester'),
      cls.FieldMapper(course.exam_form, search.AtomField, 'exam'),
      cls.FieldMapper(course.lecture_time, search.NumberField, 'lecthours'),
      cls.FieldMapper(course.recitation_time, search.NumberField, 'recithours'),
      cls.FieldMapper(course.project_time, search.NumberField, 'projhours'),
      cls.FieldMapper(course.practical_time, search.NumberField, 'practhours'),
      # TODO(bucur): Maybe consolidate these in one field?
      cls.FieldMapper(course.learning_outcomes, search.HtmlField, 'outcomes'),
      cls.FieldMapper(course.content, search.HtmlField, 'content'),
      cls.FieldMapper(course.prior_knowledge, search.HtmlField, 'prereq'),
      cls.FieldMapper(course.type_of_teaching, search.HtmlField, 'teaching'),
      cls.FieldMapper(course.bibliography, search.HtmlField, 'biblio'),
      cls.FieldMapper(course.keywords, search.HtmlField, 'keywords'),
      cls.FieldMapper(course.exam_form_detail, search.HtmlField, 'examdetail'),
      cls.FieldMapper(course.note, search.HtmlField, 'note'),
      cls.FieldMapper(course.prerequisite_for, search.HtmlField, 'prereqfor'),
      cls.FieldMapper(course.library_recomm, search.HtmlField, 'libraryrec'),
      cls.FieldMapper(course.links, search.HtmlField, 'links')
    ]
    doc_fields = []
    
    for mapper in mappings:
      field = mapper.ConstructField()
      if field:
        doc_fields.append(field)
    
    return search.Document(doc_id=str(course.key()),
                           fields=doc_fields)
  
  @classmethod  
  def _IndexDocuments(cls, index, doc_bag):
    docs, courses = zip(*doc_bag)
    
    try:
      index.add(docs)
    except apiproxy_errors.OverQuotaError:
      logging.error("Over quota error.")
      return False
    else:
      db.put(courses)
      logging.info('Added %d documents to the index.' % len(doc_bag))
      return True

  @classmethod
  def UpdateCourseIndex(cls, courses=None):
    """Update the search index for the given courses."""
    
    if not courses:
      courses = models.Course.all().filter("needs_indexing_ =", True).run()
    
    BATCH_SIZE = 50
    
    docindex = cls.GetIndex()
    doc_bag = []
    
    for course in courses:
      doc = cls._CreateDocumentForCourse(course)
      course.needs_indexing_ = False
      if len(doc_bag) == BATCH_SIZE:
        if not cls._IndexDocuments(docindex, doc_bag):
          return False
        doc_bag = [(doc, course)]
      else:
        doc_bag.append((doc, course))
    if doc_bag:
      if not cls._IndexDocuments(docindex, doc_bag):
        return False
      
    return True

  