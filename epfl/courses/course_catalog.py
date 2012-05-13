
"""Handlers for displaying course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import jinja2
import json
import os
import webapp2

from google.appengine.api import search
from google.appengine.ext import db

import static_courses

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



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Course(db.Model):
  name = db.StringProperty(required=True)
  language = db.StringProperty(required=True, choices=set(["en", "fr"]))
  teachers = db.StringListProperty()
  studies = db.StringListProperty()
  orientations = db.StringListProperty()
  urls = db.StringListProperty()
  
  
class CourseDescription(db.Model):
  title_en = db.StringProperty()
  title_fr = db.StringProperty()
  
  homepage = db.StringProperty()
  
  language = db.StringProperty(choices=set(["en", "fr"]))
  
  instructors = db.StringListProperty()
  sections = db.StringListProperty()
  
  ects_credits = db.IntegerProperty()
  course_points = db.IntegerProperty()
  exercise_points = db.IntegerProperty()
  project_points = db.IntegerProperty()
  
  objectives_en = db.TextProperty()
  objectives_fr = db.TextProperty()
  
  contents_en = db.TextProperty()
  contents_fr = db.TextProperty()
  
  bibliography = db.TextProperty()
  
  prerequisites = db.StringListProperty()
  
  grading_method = db.StringProperty(choices=set(["sem", "writ", "oral", "sem_writ", "sem_oral"]))
  grading_formula = db.StringProperty()
  
  notes = db.StringProperty()
  
  submitted_ = db.BooleanProperty()


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
      
      results = search.Index(name=INDEX_NAME).search(query_string)
      
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
    
    
class ShowcasePage(webapp2.RequestHandler):
  def get(self):
    specializations = [ ]
    
    for spec in ["IN", "SC", "SV"]:
      specializations.append({
        "spec": spec,
        "title": SPECIALIZATION_MAPPING[spec]
      })
                                     
    template = jinja_environment.get_template('showcase.html')
    self.response.out.write(template.render(specializations=specializations))
    
    
class AjaxCourses(webapp2.RequestHandler):
  def get(self):
    spec = self.request.get("spec")
    
    courses = Course.all().order('name').run()
    
    if spec:
      courses = filter(lambda course: self.IsCourseMatching(course, spec.upper()),
                       courses)
      
    response_array = []
    slide_template = jinja_environment.get_template('slide_.html')
      
    for course in courses:
      response_array.append({ "content": slide_template.render(course=course)})
    
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(json.dumps(response_array, indent=True))
    
  @staticmethod
  def IsCourseMatching(course, spec_prefix):
    for spec in course.orientations:
      if spec.startswith(spec_prefix):
        return True
      
    return False


class CoursePage(webapp2.RequestHandler):
  def get(self, course_key):
    course = db.get(course_key)
    course._language = LANGUAGE_MAPPING[course.language]
    
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
    
    docindex = search.Index(name=INDEX_NAME)
    docindex.add(documents)
    
    self.response.out.write('Created %d documents.' % len(documents))
    
  def DeleteAllDocuments(self):
    docindex = search.Index(name=INDEX_NAME)
    
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
    

class SubmitCourseDescription(webapp2.RequestHandler):
  def post(self):
    course_id = self.request.POST.get("course_id")
    course_desc = None
    
    if course_id:
      course_desc = CourseDescription.get_by_id(int(course_id))
    else:
      course_desc = CourseDescription(submitted_=False)
    
    # Submission state
    course_desc.submitted_ = (self.request.POST.get("update_btn") == "Submit")
      
    # Course title
    course_desc.title_en = self.request.POST.get("title_en", "")
    course_desc.title_fr = self.request.POST.get("title_fr", "")
    
    # Course URL
    course_desc.homepage = self.request.POST.get("url", "http://")
    
    # Language
    course_desc.language = self.request.POST.get("language", "") 
    
    # Instructors
    instructors = []
    for i in range(1, 5):
      instructor = self.request.POST.get("instructor%d" % i, "None")
      if instructor != "None":
        instructors.append(instructor)
    course_desc.instructors = instructors
    
    # Sections
    sections = set()
    if self.request.POST.get("sec_in"):
      sections.add("IN")
    if self.request.POST.get("sec_sc"):
      sections.add("SC")
    other_sections = self.request.POST.get("sec_other")
    if other_sections:
      for section in other_sections.split(","):
        sections.add(section.strip().upper())
    
    course_desc.sections = list(sections)

    # Credits
    course_desc.ects_credits = int(self.request.POST.get("ects_total", "2"))
    course_desc.course_points = int(self.request.POST.get("ects_lecture", "0h")[0:1])
    course_desc.exercise_points = int(self.request.POST.get("ects_recitation", "0h")[0:1])
    course_desc.project_points = int(self.request.POST.get("ects_project", "0h")[0:1])

    # Objectives
    course_desc.objectives_en = self.request.POST.get("objectives_en", "")
    course_desc.objectives_fr = self.request.POST.get("objectives_fr", "")
    
    # Contents
    course_desc.contents_en = self.request.POST.get("contents_en", "")
    course_desc.contents_fr = self.request.POST.get("contents_fr", "")
    
    # Bibliography
    course_desc.bibliography = self.request.POST.get("bibliography", "")
    
    # Prerequisites
    prerequisites = []
    for i in range(1, 5):
      prereq = self.request.POST.get("prereq%d" % i, "none")
      if prereq != "none":
        prerequisites.append(prereq)
    course_desc.prerequisites = prerequisites
    
    # Grading method & formula
    course_desc.grading_method = self.request.POST.get("grading_method", "")
    course_desc.grading_formula = self.request.POST.get("grading_formula", "")
    
    # Notes
    course_desc.notes = self.request.POST.get("notes", "")
    
    course_desc.put()
    
    self.redirect('/update?course_id=%d&saved=%s' % (
        course_desc.key().id(),
        "1" if self.request.POST.get("update_btn") == "Save" else ""))
      

class CourseDescriptionPage(webapp2.RequestHandler):
  def get(self):
    course_id = self.request.get("course_id")
    saved_flag = self.request.get("saved")
    course = None
    
    if course_id:
      try:
        course = CourseDescription.get_by_id(int(course_id))
      except ValueError:
        pass
      
    instr_list = ["None"]
    instr_list.extend([", ".join([inst[1], inst[0]]).decode("utf-8")
                      for inst in sorted(static_courses.INSTRUCTORS_NEW,
                                        key=lambda inst: inst[1].lower())])
    
    prereq_list = [("none", "None")]
    prereq_list.extend([(prereq[0].lower(),
                         " ".join([prereq[0], prereq[1]]).decode("utf-8"))
                        for prereq in static_courses.PREREQUISITES])
      
    template_args = {
      'course': course,
      'saved': saved_flag,
      'instructors': instr_list,
      'prerequisites': prereq_list,
      
      'instr_values': ['None', 'None', 'None', 'None'],
      
      'prereq_values': ['none', 'none', 'none', 'none'],
      
      'sec_in': 'IN' in course.sections if course else None,
      'sec_sc': 'SC' in course.sections if course else None,
      'sec_other': ', '.join(filter(lambda sec: sec not in ['IN', 'SC'],
                                     course.sections)) if course else None
    }
    
    if course:
      for i in range(len(course.instructors)):
        template_args["instr_values"][i] = course.instructors[i]
      
      for i in range(len(course.prerequisites)):
        template_args['prereq_values'][i] = course.prerequisites[i]
    
    template = jinja_environment.get_template('coursedesc.html')
    self.response.out.write(template.render(template_args))


app = webapp2.WSGIApplication([
   webapp2.Route('/', handler=ShowcasePage, name='showcase'),
   webapp2.Route('/catalog', handler=CatalogPage, name='catalog'),
   webapp2.Route('/c/<course_key>', handler=CoursePage, name='course'),
   webapp2.Route('/ajax/courses', handler=AjaxCourses, name='ajax_course'),
   webapp2.Route('/admin/search', handler=BuildSearchIndex, name='search_index'),
   webapp2.Route('/admin/submit', handler=SubmitCourseDescription, name='submit_course'),
   webapp2.Route('/update', handler=CourseDescriptionPage, name='csp')], debug=True)

