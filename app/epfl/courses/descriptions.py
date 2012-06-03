#!/usr/bin/env python

"""Course description updates."""

import logging
import StringIO
import xlwt

from google.appengine.ext import db

from epfl.courses import base_handler
from epfl.courses import static_data

authenticated = base_handler.BaseCourseDescriptionHandler.authenticated


class CourseDescription(db.Model):
  # TODO(bucur): Add default values
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
  
  grading_method = db.StringProperty(choices=set(["sem", "writ", "oral",
                                                  "sem_writ", "sem_oral"]))
  grading_formula = db.StringProperty()
  
  notes = db.TextProperty()
  
  # Metadata
  submitted_ = db.BooleanProperty()
  in_progress_ = db.BooleanProperty()
  
  created_time_ = db.DateTimeProperty(auto_now_add=True)
  last_modified_time_ = db.DateTimeProperty(auto_now=True)
  last_modified_by_ = db.TextProperty()


class LogoutHandler(base_handler.BaseCourseDescriptionHandler):
  logout_url = r"https://tequila.epfl.ch/cgi-bin/tequila/logout"
  
  @authenticated
  def get(self):
    self.session.clear()
    self.redirect(self.logout_url)


class SubmitCourseDescription(base_handler.BaseCourseDescriptionHandler):
  @authenticated
  def post(self):    
    course_id = self.request.POST.get("course_id")
    course_desc = None
    
    if course_id:
      course_desc = CourseDescription.get_by_id(int(course_id))
    else:
      course_desc = CourseDescription(submitted_=False, in_progress_=False)
      
    if not course_desc.submitted_:
      self.PopulateCourseDesc(course_desc)
    
    # Submission status
    if self.request.POST.get("update_btn") == "Submit":
      course_desc.submitted_ = True
    if self.request.POST.get("update_btn") == "Save":
      course_desc.in_progress_ = True
      
    # Author of modifications
    course_desc.last_modified_by_ = self.user_name
    
    course_desc.put()
    
    self.redirect('/update?course_id=%d' % course_desc.key().id())
    
  def PopulateCourseDesc(self, course_desc):
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
      

class CourseDescriptionPage(base_handler.BaseCourseDescriptionHandler):
  def get(self):
    """Authentication is done explicitly, inside the handler."""
    
    course = None
    course_id = self.request.get('course_id')
    if course_id:
      try:
        course_id = int(course_id)
      except ValueError:
        return self.HandleCourseNotFound()
    
    if not self.Authenticate():
      # Save the state in order to restore it after Tequilla redirects back
      self.session['course_id'] = course_id
      self.RedirectTequilla()
      return
    
    if not course_id:
      # If there is some saved state, restore it, and redirect us on
      # the right track
      if self.session.get('course_id'):
        self.redirect('/update?course_id=%d' % self.session['course_id'])
        self.session.pop('course_id')
        return
    
    if course_id:
      course = CourseDescription.get_by_id(course_id)
      if not course:
        return self.HandleCourseNotFound(course_id)
      
    instr_list = ["None"]
    instr_list.extend([", ".join([inst[1], inst[0]]).decode("utf-8")
                      for inst in sorted(static_data.INSTRUCTORS_NEW,
                                        key=lambda inst: inst[1].lower())])
    
    prereq_list = [("none", "None")]
    prereq_list.extend([(prereq[0].lower(),
                         " ".join([prereq[0], prereq[1]]).decode("utf-8"))
                        for prereq in static_data.PREREQUISITES])
      
    template_args = {
      'course': course,
      'login': self.user_name,
      'saved': "saved" in self.session.get_flashes(),
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
    
    self.RenderTemplate('coursedesc.html', template_args)
    
  def HandleCourseNotFound(self, course_id=None):
    self.error(400)
    self.RenderTemplate('course_not_found.html', { "course_id": course_id })
    
class DumpCSVHandler(base_handler.BaseCourseDescriptionHandler):
  class ColumnMapping(object):
    def __init__(self, column_name, field_name, is_list, mapping, width=None):
      self.column_name = column_name
      self.field_name = field_name
      self.is_list = is_list
      self.mapping = mapping
      self.width = width
      
    def _GetMappedValue(self, value):
      if self.mapping:
        value = self.mapping.get(value, value)
        
      if isinstance(value, basestring):
        value = value.replace("\r", "")

      return value
      
    def GetText(self, course_desc):
      if self.is_list:
        return ", ".join([self._GetMappedValue(x)
                          for x in getattr(course_desc, self.field_name, [])])
      else:
        return self._GetMappedValue(getattr(course_desc, self.field_name, ""))
      
  @authenticated
  def get(self):
    logging.info("Course data accessed by %s" % self.user_name)
    
    self.response.headers['Content-Type'] = 'application/vnd.ms-excel'
    self.response.headers['Content-Disposition'] = 'attachment;filename=data.xls'
    
    columns = [
      self.ColumnMapping('Title (en)', 'title_en', False, None, 40),
      self.ColumnMapping('Title (fr)', 'title_fr', False, None, 40),
      self.ColumnMapping('Instructor(s)', 'instructors', True, None, 20),
      self.ColumnMapping('Language', 'language', False,
                         static_data.LANGUAGE_CODE),
      self.ColumnMapping('Section(s)', 'sections', True, None),
      self.ColumnMapping('ECTS Credits', 'ects_credits', False, None),
      self.ColumnMapping('Course hours', 'course_points', False, None),
      self.ColumnMapping('Exercise hours', 'exercise_points', False, None),
      self.ColumnMapping('Project hours', 'project_points', False, None),
      self.ColumnMapping('Objectives (en)', 'objectives_en', False, None, 70),
      self.ColumnMapping('Objectives (fr)', 'objectives_fr', False, None, 70),
      self.ColumnMapping('Contents (en)', 'contents_en', False, None, 100),
      self.ColumnMapping('Contents (fr)', 'contents_fr', False, None, 100),
      self.ColumnMapping('Prerequisites', 'prerequisites', True,
                         dict([(x.lower(), "(%s) %s" % (x, y.decode("utf-8")))
                               for (x, y) in static_data.PREREQUISITES]), 40),
      self.ColumnMapping('Form of teaching', 'form_of_teaching', False, None, 30),
      self.ColumnMapping('Grading method', 'grading_method', False,
                         static_data.GRADING_CODE, 30),
      self.ColumnMapping('Grading formula', 'grading_formula', False, None, 20),
      self.ColumnMapping('URL', 'homepage', False, None, 40),
      self.ColumnMapping('Bibliography', 'bibliography', False, None, 50),
      self.ColumnMapping('Notes', 'notes', False, None, 50),
    ]
    
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Desc 2012-2013')
    sheet.set_panes_frozen(True) # frozen headings instead of split panes
    sheet.set_horz_split_pos(1) # in general, freeze after last heading row
    sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
    
    style = xlwt.easyxf("font: bold on;")
    
    for i, column in enumerate(columns):
      sheet.write(0, i, column.column_name, style)
      if column.width:
        sheet.col(i).width = column.width * 256
        
    style = xlwt.easyxf("alignment: wrap on;")
    
    row_index = 1
    for course_desc in CourseDescription.all().filter("submitted_", True).run():
      form_of_teaching = []
      if course_desc.course_points > 0:
        form_of_teaching.append("Ex cathedra")
      if course_desc.exercise_points > 0:
        form_of_teaching.append("Exercices")
      if course_desc.project_points > 0:
        form_of_teaching.append("Project")
      course_desc.form_of_teaching = " + ".join(form_of_teaching) 
      
      for i, column in enumerate(columns):
        sheet.write(row_index, i, column.GetText(course_desc), style)
      row_index += 1
        
    buffer = StringIO.StringIO()
    workbook.save(buffer)
    
    self.response.out.write(buffer.getvalue())
    

