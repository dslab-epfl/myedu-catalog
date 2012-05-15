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

class ISAParser(object):
  def __init__(self):
    self.total_courses = 0
    
    self.total_titles = 0
    self.total_semesters = 0
    self.total_credit_info = 0
    
    self.total_para = {}
  
  def _SanitizeContent(self, content):
    content = content.replace("&amp;", "&")
    content = content.replace("&nbsp;", " ")
    
    return " ".join([x.strip() for x in content.split('\n')])
  
  def _ParseDescriptionParagraph(self, html_data, para_name):
    try:
      para = html_data.split("<h4>%s</h4>" % para_name, 1)[1].split('</p>', 1)[0]
      para = re.split(r'<p id="ID[0-9]+">', para, 1)[1]
      para = self._SanitizeContent(para)
      
      if para:
        self.total_para[para_name] = self.total_para.get(para_name, 0) + 1
        
      return para
    except IndexError:
      logging.error("Could not parse description para '%s'" % para_name)
  
  def _ParseCourseTitle(self, html_data):
    try:
      title = html_data.split('<h2 class="noSpacing">', 1)[1].split('</h2>', 1)[0].strip()
      title = self._SanitizeContent(title)
      
      if title:
        self.total_titles += 1
        
      return title
    except IndexError:
      logging.error("Could not parse course title")
  
  def _ParseSemester(self, html_data):
    try:
      semester = html_data.split('<strong>Semester</strong>', 1)[1].split('</li>', 1)[0]
      semester = semester.rsplit('</div>', 1)[1]
      semester = self._SanitizeContent(semester)
      
      if semester:
        self.total_semesters += 1
      
      return semester
    except IndexError:
      logging.error("Could not parse semester")
      
  def _ParseCreditInfo(self, html_data):
    try:
      credit = html_data.split('<strong>Credits</strong>', 1)[1].split('</span></li>', 1)[0]
      credit = credit.rsplit('<span class="nbCredits">', 1)[1]
      credit = self._SanitizeContent(credit)
      
      if credit:
        self.total_credit_info += 1
      
      return credit
    except IndexError:
      logging.error("Could not parse credit info")

  def ParseHTMLData(self, html_data):
    info = {
      "title": self._ParseCourseTitle(html_data),
      "semester": self._ParseSemester(html_data),
      "credits": self._ParseCreditInfo(html_data),
      "learning_outcomes": self._ParseDescriptionParagraph(html_data,
                                                           "Learning outcomes"),
      "content": self._ParseDescriptionParagraph(html_data, "Content"),
      "keywords": self._ParseDescriptionParagraph(html_data, "Keywords"),
      "prior_knowledge": self._ParseDescriptionParagraph(html_data,
                                                         "Required prior knowledge"),
      "type_of_teaching": self._ParseDescriptionParagraph(html_data,
                                                          "Type of teaching"),
      "form_of_examination": self._ParseDescriptionParagraph(html_data,
                                                             "Form of examination"),
      "bibliography": self._ParseDescriptionParagraph(html_data, "Bibliography and material")
    }
    
    self.total_courses += 1
    
    return info
  
  def ShowStatistics(self):
    stat_dict = {
      "total_courses": self.total_courses,
      "total_titles": self.total_titles,
      "total_semesters": self.total_semesters,
      "total_credit_info": self.total_credit_info,
      "total_para": self.total_para
    }
    pprint.pprint(stat_dict)


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
    logging.info("Processing '%s'" % course["title"])
    
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
      
      if not (info["semester"] and info["credits"]):
        logging.warning("Could not find some information at %s" % course["urls"])
        
      if info["title"] != course["title"]:
        logging.warning("Course titles differ at %s: '%s' '%s'" 
                        % (course["urls"], info["title"], course["title"]))
        
  isa_parser.ShowStatistics()

if __name__ == "__main__":
  main()