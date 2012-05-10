
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import os
import webapp2

from google.appengine.api import search
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

language_mapping = {
  "en": "English",
  "fr": "French"
}

index_name = 'courses-index'


class Course(db.Model):
  name = db.StringProperty(required=True)
  language = db.StringProperty(required=True, choices=set(["en", "fr"]))
  teachers = db.StringListProperty()
  studies = db.StringListProperty()
  orientations = db.StringListProperty()
  urls = db.StringListProperty()


class CatalogPage(webapp2.RequestHandler):
  def get(self):
    # Check first whether we show search results instead
    search_query = self.request.get("query")
    search_title = self.request.get("title")
    search_teacher = self.request.get("teacher")
    
    courses = None
    is_search = False
    
    if search_title or search_teacher or search_query:
      query_string = "%s %s %s" % (search_query,
                                   ("title:%s" % search_title) if search_title else "",
                                   ("teacher:%s" % search_teacher) if search_teacher else "")
      
      results = search.Index(name=index_name).search(query_string)
      
      courses = db.get([document.doc_id for document in results])
      is_search = True
    else:
      courses = Course.all().order('name').run()
    
    template_args = {
      'courses': courses,
      'is_search': is_search,
    }
    template = jinja_environment.get_template('catalog.html')
    self.response.out.write(template.render(template_args))


class CoursePage(webapp2.RequestHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course._language = language_mapping[course.language]
    
    template = jinja_environment.get_template('course.html')
    self.response.out.write(template.render(course=course))
    

class BuildSearchIndex(webapp2.RequestHandler):
  def get(self):
    template = jinja_environment.get_template('build_index.html')
    self.response.out.write(template.render())
  
  def post(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.DeleteAllDocuments()
    self.CreateAllDocuments()
    
  def CreateAllDocuments(self):
    courses = Course.all().run()
    documents = [self.CreateDocument(course) for course in courses]
    
    docindex = search.Index(name=index_name)
    docindex.add(documents)
    
    self.response.out.write('Created %d documents.' % len(documents))
    
  def DeleteAllDocuments(self):
    docindex = search.Index(name=index_name)
    
    while True:
      document_ids = [document.doc_id
                      for document in docindex.list_documents(ids_only=True)]
      if not document_ids:
        break
      docindex.remove(document_ids)
      self.response.out.write('Removed %d documents.\n' % len(document_ids))
    
  def CreateDocument(self, course):
    return search.Document(doc_id=str(course.key()),
                           fields=[search.TextField(name='title', 
                                                    value=course.name),
                                   search.TextField(name='teacher',
                                                    value=", ".join(course.teachers))])


app = webapp2.WSGIApplication([
   webapp2.Route('/', handler=CatalogPage, name='home'),
   webapp2.Route('/c/<course_key>', handler=CoursePage, name='course'),
   webapp2.Route('/admin/search', handler=BuildSearchIndex, name='search_index')], debug=True)
