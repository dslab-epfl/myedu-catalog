#!/usr/bin/env python

"""Parses already crawled HTML files, and extracts course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import json
import logging
import os
import pprint
import re

COURSE_DESC_FILE = os.path.join(os.path.dirname(__file__),
                                'course_info.json')

PARSED_DATA_FILE = os.path.join(os.path.dirname(__file__),
                                'parser_output.json')

class ISAParser(object):
  def __init__(self):
    self.stat_dict = {}
    
  def _UpdateStat(self, stat_name, content):
    if content:
      self.stat_dict[stat_name] = self.stat_dict.get(stat_name, 0) + 1
  
  def _SanitizeContent(self, content):
    replacement_map = {
      "[/b]": "</b>", 
      "[/i]": "</i>", 
      "[b]": "<b>", 
      "[br/]": "<br/>", 
      "[br]": "<br/>", 
      "[i]": "<i>", 
      "[li]": "<li>"
    }
    content = content.replace("&amp;", "&")
    content = content.replace("&nbsp;", " ")
    
    tags = re.findall(r"\[[^\[]*?\]", content)
    
    for tag in tags:
      if len(tag) > 7: # Empirical classification of square paren
        continue
      if tag in replacement_map:
        content = content.replace(tag, replacement_map[tag])
      else:
        content = content.replace(tag, "")
        
    
    return " ".join([x.strip() for x in content.split('\n')]).strip()
  
  def _ParseDescriptionParagraph(self, html_data, para_name):
    try:
      para = html_data.split("<h4>%s</h4>" % para_name, 1)[1].split('</p>', 1)[0]
      para = re.split(r'<p id="ID[0-9]+">', para, 1)[1]
      para = self._SanitizeContent(para)
      
      self._UpdateStat(para_name, para)        
      return para
    except IndexError:
      logging.error("Could not parse description para '%s'" % para_name)
      
  def _ParseCourseHours(self, html_data, name):
    try:
      hours = html_data.split("<strong>%s</strong>" % name, 1)[1].split('</li>', 1)[0]
      hours = self._SanitizeContent(hours)
      
      if not hours:
        return
      
      match = re.search(r"(\d+).*?(\d+)", hours)
      
      if not match:
        return
      
      result = int(match.group(1))
      
      self._UpdateStat(name, result)
      
      return result
    except IndexError:
      logging.error("Could not parse %s course hours" % name)
  
  def _ParseCourseTitle(self, html_data):
    try:
      title = html_data.split('<h2 class="noSpacing">', 1)[1].split('</h2>', 1)[0].strip()
      title = self._SanitizeContent(title)
      
      self._UpdateStat("Title", title)
        
      return title
    except IndexError:
      logging.error("Could not parse course title")
  
  def _ParseSemester(self, html_data):
    try:
      semester = html_data.split('<strong>Semester</strong>', 1)[1].split('</li>', 1)[0]
      semester = semester.rsplit('</div>', 1)[1]
      semester = self._SanitizeContent(semester)
      
      self._UpdateStat("Semester", semester)
      
      return semester
    except IndexError:
      logging.error("Could not parse semester")
      
  def _ParseCreditInfo(self, html_data):
    try:
      credit = html_data.split('<strong>Credits</strong>', 1)[1].split('</span></li>', 1)[0]
      credit = credit.rsplit('<span class="nbCredits">', 1)[1]
      credit = self._SanitizeContent(credit)
      
      self._UpdateStat("Credits", credit)
      
      if not credit:
        return
      
      return int(credit)
    except IndexError:
      logging.error("Could not parse credit info")
      
  def _ParseExamForm(self, html_data):
    try:
      exam_form = html_data.split('<strong>Exam form</strong>', 1)[1].split('</li>', 1)[0]
      exam_form = exam_form.rsplit('</div>', 1)[1]
      exam_form = self._SanitizeContent(exam_form)
      
      self._UpdateStat("Exam form", exam_form)

      return exam_form
    except IndexError:
      logging.error("Could not parse exam form")

  def ParseHTMLData(self, html_data):
    info = {
      "title": self._ParseCourseTitle(html_data),
      "semester": self._ParseSemester(html_data),
      "credit_count": self._ParseCreditInfo(html_data),
      "learning_outcomes": self._ParseDescriptionParagraph(html_data,
                                                           "Learning outcomes"),
      "content": self._ParseDescriptionParagraph(html_data, "Content"),
      "keywords": self._ParseDescriptionParagraph(html_data, "Keywords"),
      "prior_knowledge": self._ParseDescriptionParagraph(html_data,
                                                         "Required prior knowledge"),
      "type_of_teaching": self._ParseDescriptionParagraph(html_data,
                                                          "Type of teaching"),
      "exam_form_detail": self._ParseDescriptionParagraph(html_data,
                                                             "Form of examination"),
      "bibliography": self._ParseDescriptionParagraph(html_data, "Bibliography and material"),
      
      "exam_form": self._ParseExamForm(html_data),
      "lecture_time": self._ParseCourseHours(html_data, "Lecture"),
      "recitation_time": self._ParseCourseHours(html_data, "Recitation"),
      "project_time": self._ParseCourseHours(html_data, "Project"),
      "practical_time": self._ParseCourseHours(html_data, "Practical work")
    }
    
    self._UpdateStat("Courses", info)
    
    return info
  
  def ShowStatistics(self):
    pprint.pprint(self.stat_dict)


def main():
  logging.basicConfig(level=logging.INFO)
  
  course_data = None
  with open(COURSE_DESC_FILE, "r") as f:
    course_data = json.load(f, encoding="utf-8")
    
  if not course_data:
    logging.error("No course data found")
    return
  
  counters = {}
  
  isa_parser = ISAParser()
  
  for course in course_data:
    counters[course["id"]] = counters.get(course["id"], 0) + 1
    logging.info("Processing '%s' at %s" % (course["title"], course["urls"]))
    
    html_data = None
    
    try:
      file_name = os.path.join(
          os.path.dirname(__file__),
          "html-data",
          "%s-%d.html" % (course["id"], counters[course["id"]]))
      
      with open(file_name, "r") as f:
        html_data = f.read().decode("iso-8859-1")
    except IOError:
      logging.warning("Could not open the HTML file '%s'" % file_name)
      
    if html_data:
      info = isa_parser.ParseHTMLData(html_data)
        
      if info["title"] != course["title"]:
        logging.warning("Course titles differ at %s: '%s' '%s'" 
                        % (course["urls"], info["title"], course["title"]))
        
      course["info"] = info
      
  aggregated_data = {}
  mismatches = 0
  mismatched_keys = set()
  mismatched_courses = set()
  
  for course in course_data:
    agg_course = aggregated_data.setdefault(course["id"], {
      "id": course["id"],
      "title": course["title"],
      "info": {}
    })
    
    for key, value in course["info"].iteritems():
      if not value:
        continue
      
      if key not in agg_course["info"] or not agg_course["info"][key]:
        agg_course["info"][key] = value
      elif key in agg_course["info"] and value != agg_course["info"][key]:
        logging.warning("Conflicting information for course %s at '%s'" 
                        % (course["title"], course["urls"]))
        logging.warning("Mismatched key %s" % key)
        logging.warning("First value: %s" % (value,))
        logging.warning("Second value: %s" % (agg_course["info"][key],))
        mismatches += 1
        mismatched_keys.add(key)
        mismatched_courses.add(course["title"])
        
  logging.info("Mismatches: %d" % mismatches)
  logging.info("Mismatched keys: %s" % mismatched_keys)
  logging.info("Mismatched courses: %s" % mismatched_courses)
      
  with open(PARSED_DATA_FILE, "w") as f:
    json.dump(sorted(aggregated_data.values(), key=lambda course: course["title"]),
              f, indent=True, encoding="utf-8")
        
  isa_parser.ShowStatistics()

if __name__ == "__main__":
  main()