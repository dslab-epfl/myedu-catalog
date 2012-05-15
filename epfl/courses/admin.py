#!/usr/bin/env python

"""Administration tasks."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import csv
import jinja2
import json
import logging
import os
import webapp2


from google.appengine.api import search
from google.appengine.ext import db

from epfl.courses import models


COURSES_DATA_FILE = "data/all_epfl_import.csv"

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class BuildSearchIndex(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('build_index.html')
    self.response.out.write(template.render())
  
  def post(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.DeleteAllDocuments()
    self.CreateAllDocuments()
    
    
class StatsHandler(webapp2.RequestHandler):
  pass


class DumpHandler(webapp2.RequestHandler):
  """Shamelessly dumps the entire course information."""
  def get(self):
    results = models.Course.all().run(projection=('title', 'urls'))
    
    data = [{ "id": str(course.key()), "title": course.title, "urls": course.urls[0]}
            for course in results]
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(data, indent=True, encoding="utf-8"))


class ReinitDataHandler(webapp2.RequestHandler):
  INVALID_SCIPER = 126096
  
  def NormalizeRow(self, row):
    def clean_up(field):
      return field.decode("utf-8").strip().replace("\n", "")
    def split_multiple(field):
      return map(lambda x: clean_up(x), field.split("#"))
    
    row["title"] = clean_up(row["title"])
    row["language"] = clean_up(row["language"])
    row["study_plans"] = split_multiple(row["study_plans"])
    
    if row["scipers"]:
      row["scipers"] = map(int, split_multiple(row["scipers"]))
      row["instructors"] = split_multiple(row["instructors"])
    else:
      row["scipers"] = []
      row["instructors"] = []
    
    row["sections"] = split_multiple(row["sections"])
    row["urls"] = split_multiple(row["urls"])
    
  def BuildAllCourses(self):
    logging.info('Loading course catalog information')
    
    reader = csv.DictReader(
        open(COURSES_DATA_FILE, "rU"),
        ["_empty", "title", "language", "study_plans", "scipers", "instructors",
         "sections", "urls"])
    
    skip_flag = True
    
    empty_line_count = 0
    no_instructor_count = 0
    invalid_course_titles = []
    
    all_courses = []
    
    for row in reader:
      if not row["language"]:
        empty_line_count += 1
        continue
      if skip_flag:
        skip_flag = False
        continue
      
      try:
        self.NormalizeRow(row)
        if not row["scipers"]:
          no_instructor_count += 1
        all_courses.append(self.BuildCourse(row))
      except:
        raise
        invalid_course_titles.append(row["title"])
        
    db.put(all_courses)
    
    self.response.out.write("Created %d courses.\n" % len(all_courses))
    
    self.response.out.write("Empty lines: %d\n" % empty_line_count)
    self.response.out.write("Unspecified instructor courses: %d\n" % no_instructor_count)
    self.response.out.write("Invalid courses: %s\n" % invalid_course_titles)
    
  def BuildCourse(self, row):
    instructors = row["instructors"]
    if row["scipers"] and row["scipers"][0] == self.INVALID_SCIPER:
      instructors = ["multi"]
       
    return models.Course(
        title=row["title"],
        language=row["language"],
        instructors=instructors,
        sections=row["sections"],
        study_plans=row["study_plans"],
        urls=row["urls"])
    
  def DeleteAllCourses(self):
    course_keys = models.Course.all(keys_only=True).fetch(None)
    db.delete(course_keys)
    
    self.response.out.write("Deleted %d courses.\n" % len(course_keys))
    
  def DeleteAllDocuments(self):
    docindex = search.Index(name=models.INDEX_NAME)
    
    while True:
      document_ids = [document.doc_id
                      for document in docindex.list_documents(ids_only=True)]
      if not document_ids:
        break
      docindex.remove(document_ids)
      logging.info('Removed %d documents.' % len(document_ids))
      
  def CreateAllDocuments(self):
    BATCH_SIZE = 50
    
    docindex = search.Index(name=models.INDEX_NAME)
    
    doc_bag = []
    
    for course in models.Course.all().run():
      doc = self.CreateDocument(course)
      if len(doc_bag) == BATCH_SIZE:
        docindex.add(doc_bag)
        logging.info('Added %d documents to the index.' % len(doc_bag))
        doc_bag = [doc]
      else:
        doc_bag.append(doc)
    if doc_bag:
      docindex.add(doc_bag)
      logging.info('Added %d documents to the index.' % len(doc_bag))
    
  def CreateDocument(self, course):
    return search.Document(doc_id=str(course.key()),
                           fields=[search.TextField(name='title', 
                                                    value=course.title),
                                   search.TextField(name='instructor',
                                                    value=", ".join(course.instructors)),
                                   search.TextField(name='section',
                                                    value=", ".join(course.sections))])
    
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    
    if self.request.get("all"):
      logging.info("Deleting all course information")
      self.DeleteAllCourses()
      
    self.DeleteAllDocuments()
    
    if self.request.get("all"):
      self.BuildAllCourses()
      
    self.CreateAllDocuments()
    
    self.response.out.write('OK.\n')
