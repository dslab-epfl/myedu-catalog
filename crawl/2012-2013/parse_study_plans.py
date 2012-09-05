#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

# pylint: disable-msg=W0311

"""Parse the 2012-2013 course descriptions starting from study plan URLs."""

__author__ = "stefan.bucur@epfl.ch"

import contextlib
import logging
import os
import re
import urllib
import urlparse

from bs4 import BeautifulSoup

import caching


# The root of our parsing
search_base_url = "http://search-test.epfl.ch"
study_plans_url = urlparse.urljoin(search_base_url, "/eduweb.action")


this_dir = os.path.dirname(__file__)

# Cached computations
study_plans_path = os.path.join(this_dir, "study_plans.json")
course_list_path = os.path.join(this_dir, "course_list.json")
course_desc_path = os.path.join(this_dir, "course_desc.json")


def _ProcessStudyPlan(plan_id, plan_name, plan_soup, id_trim_size=3):
  """Process a study plan soup."""

  sections = []
  for list_item in plan_soup.find_all('li'):
    section_id = "-".join(list_item['id'].split("_")[id_trim_size:]).upper()
    section_title = list_item.a.string.strip()
    section_url = search_base_url + list_item.a["href"]

    sections.append({
      "id": section_id,
      "title": section_title,
      "url": section_url,
    })

  return {
    "id": plan_id,
    "name": plan_name,
    "sections": sections,
  }


@caching.CachedJSON(study_plans_path)
def FetchStudyPlans():
  """Fetch all study plans from the EPFL search site."""

  study_plans_html = caching.CachedURLGet(study_plans_url)

  plans = []

  soup = BeautifulSoup(study_plans_html)
  # Propedeutics
  prop_sections = soup.find('li', id='bama_prop')
  plans.append(_ProcessStudyPlan("prop", "Propedeutics", prop_sections))

  # Bachelor
  bachelor_sections = soup.find('li', id='bama_cyclebachelor')
  plans.append(_ProcessStudyPlan("bachelor", "Bachelor", bachelor_sections))

  # Master
  master_sections = soup.find('li', id='bama_cyclemaster')
  plans.append(_ProcessStudyPlan("master", "Master", master_sections))

  # Doctoral
  phd_sections = soup.find('li', id='edoc')
  plans.append(_ProcessStudyPlan("edoc", "Doctoral", phd_sections,
                                 id_trim_size=2))

  # Minor
  minor_sections = soup.find('li', id='min_')
  plans.append(_ProcessStudyPlan("min", "Minor", minor_sections))

  return {
    "plans": plans
  }


def _FetchCoursesInSection(plan_id, section_id, section_url):
  section_html = caching.CachedURLGet(section_url)

  soup = BeautifulSoup(section_html)

  courses = []

  for course_entry in soup.find_all("div", class_="cours-name"):
    if course_entry.a is None:
      continue

    course_name = course_entry.a.string.strip()
    course_url = course_entry.a["href"]

    # A valid course URL points to the IS Academia website
    parsed_url = urlparse.urlsplit(course_url)
    if parsed_url.netloc != "isa.epfl.ch":
      print "-- Invalid course entry for ", course_name, "at", course_url
      continue

    course_url_fr = re.sub(r"ww_c_langue=en", "ww_c_langue=fr", course_url)

    courses.append({
      "title": course_name,
      "url": course_url,
      "url_fr": course_url_fr,
      "plan": plan_id,
      "section": section_id,
    })

  return courses


@caching.CachedJSON(course_list_path)
def FetchCourseList(study_plans):
  course_list = []

  for plan in study_plans["plans"]:
    for section in plan["sections"]:
      courses = _FetchCoursesInSection(plan["id"], section["id"],
                                       section["url"])
      course_list.extend(courses)

  return {
    "courses": course_list
  }


def ShowCourseListStatistics(courses):
  course_list = courses["courses"]

  title_set = set()
  for course in course_list:
    title_set.add(course["title"])

  print "Total courses:", len(course_list)
  print "Unique course titles:", len(title_set)
  

class ParsingError(Exception):
  """Occurs when the parser doesn't recognize the page structure."""
  
  pass


class ParsedCourseDescription(object):
  """Parse the soup of a course description page."""

  # English titles for subsections
  lecturer_title = "Lecturer"
  language_title = "Language"
  links_title = "Links"
  library_rec_title = "The library recommends"

  semester_label = "Semester"
  exam_form_label = "Exam form"
  credits_label = "Credits"
  hpw_label = "Hour(s) per week x 14 weeks"
  coefficient_label = "Coefficient"
  subjects_label = "Subject examined"
  lecture_label = "Lecture"
  recitation_label = "Recitation"
  project_label = "Project"
  labs_label = "Labs"
  practical_label = "Practical work"

  # Make this a set, for quick lookup
  free_text_titles = set([
    "Prerequisite for",
    "Learning outcomes",
    "Content",
    "Type of teaching",
    "Form of examination",
    "Keywords",
    "Required prior knowledge",
    "Bibliography and material",
    "Note",
  ])

  week_hours_re = re.compile(r"(\d+)\s+Hour\(s\) per week x (\d+) weeks",
                             flags=re.UNICODE)
  sem_hours_re = re.compile(r"(\d+)\s+Hour\(s\) per semester",
                            flags=re.UNICODE)
  total_hours_re = re.compile(r"(\d+)\s+Hour\(s\)",
                              flags=re.UNICODE)

  def __init__(self, soup, err_on_unknown=True):
    self._soup = soup
    self._err_on_unknown = err_on_unknown

    self.title = None
    self.instructors = []
    self.language = None

    self.semester = None
    self.credits = None
    self.coefficient = None
    self.exam_form = None

    self.lecture_hours = None
    self.recitation_hours = None
    self.project_hours = None
    self.lab_hours = None
    self.practical_hours = None

    self.free_text_desc = []
    self.links = []
    self.library_rec = None

    self.unknown_subsections = set()
    self.unknown_labels = set()

  def _ParseLecturer(self, subsection):
    """Populate the instructor list."""

    for entry in subsection.next_siblings:
      if entry.name == "h4":
        break
      elif entry.name == "a":
        self.instructors.append((entry.string.strip(), entry["href"]))

  def _ParseLanguage(self, subsection):
    """Populate the language field."""

    for entry in subsection.next_siblings:
      if entry.name == "h4":
        break
      elif entry.name == "p":
        self.language = entry.string.strip()
        break

  def _ParseLinks(self, subsection):
    """Populate the links field."""

    for entry in subsection.next_siblings:
      if entry.name == "h4":
        break
      elif entry.name == "a":
        self.links.append((entry.string.strip(), entry["href"]))

  def _ParseLibraryRec(self, subsection):
    """Parse library recommendations."""

    for entry in subsection.next_siblings:
      if entry.name == "h4":
        break
      elif entry.name == "ul":
        self.library_rec = unicode(entry)
        break

  def _ParseFreeText(self, subsection):
    """Parse a free-text description."""

    title = subsection.string.strip()

    for entry in subsection.next_siblings:
      if entry.name == "h4":
        break
      elif entry.name == "p":
        contents = "".join(entry.contents)

    self.free_text_desc.append((title, contents))

  def _ParseMainContent(self):
    main_content = self._soup.find(id="content")

    # Title
    self.title = main_content.h2.string.strip()

    # Subsections
    for subsection in main_content.find_all("h4"):
      subsection_title = subsection.string.strip()

      if self.lecturer_title in subsection_title:
        self._ParseLecturer(subsection)
      elif self.language_title in subsection_title:
        self._ParseLanguage(subsection)
      elif self.links_title in subsection_title:
        self._ParseLinks(subsection)
      elif subsection_title in self.free_text_titles:
        self._ParseFreeText(subsection)
      elif subsection_title in self.library_rec_title:
        self._ParseLibraryRec(subsection)
      else:
        self.unknown_subsections.add(subsection_title)
        if self._err_on_unknown:
          raise ParsingError("Unrecognized section name '%s'" % subsection_title)

  @classmethod
  def _ParseCourseHours(cls, value):
    match = cls.week_hours_re.match(value)
    if match:
      return {
        "week_hours": int(match.group(1)),
        "weeks": int(match.group(2)),
      }

    match = cls.sem_hours_re.match(value)
    if match:
      return {
        "total_hours": int(match.group(1)),
      }

    match = cls.total_hours_re.match(value)
    if match:
      return {
        "total_hours": int(match.group(1)),
      }
      
    raise ParsingError("Invalid course hours: '%s'" % value)

  def _ParseSideBar(self):
    side_bar = self._soup.find(class_="right-col")
    first_plan = side_bar.find("ul").find("ul")

    if not first_plan:
      return

    for item in first_plan.find_all("li"):
      if not item.strong.string:
        continue

      item_label = item.strong.string.strip()
      item_value = " ".join([s for s in item.stripped_strings
                             if s != item_label])

      if not item_value:
        print "** Empty item value for '%s'" % item_label
        continue

      print item_label, "=", item_value

      # TODO(bucur): Move string constants to class definition, to support
      # French in the future.
      if item_label == self.semester_label:
        self.semester = item_value
      elif item_label == self.exam_form_label:
        self.exam_form = item_value
      elif (item_label == self.credits_label
            or item_label == self.hpw_label):
        self.credits = int(item_value)
      elif item_label == self.coefficient_label:
        self.coefficient = float(item_value)
      elif item_label == self.subjects_label:
        pass # Ignored
      elif item_label == self.lecture_label:
        self.lecture_hours = self._ParseCourseHours(item_value)
      elif item_label == self.recitation_label:
        self.recitation_hours = self._ParseCourseHours(item_value)
      elif item_label == self.project_label:
        self.project_hours = self._ParseCourseHours(item_value)
      elif item_label == self.labs_label:
        self.lab_hours = self._ParseCourseHours(item_value)
      elif item_label == self.practical_label:
        self.practical_hours = self._ParseCourseHours(item_value)
      else:
        self.unknown_labels.add(item_label)
        if self._err_on_unknown:
          raise ParsingError("Unrecognized item label '%s'" % item_label)

  def ParseDescription(self):
    """Populate all course fields."""

    self._ParseMainContent()
    self._ParseSideBar()
    
    
class ParsedCourseDescriptionFrench(ParsedCourseDescription):
  """Parse French course descriptions."""
  
  lecturer_title = u"Enseignant"
  language_title = u"Langue"
  links_title = u"Liens"
  library_rec_title = u"La bibliothèque vous propose"

  semester_label = u"Semestre"
  exam_form_label = u"Forme de l'examen"
  credits_label = u"Crédits"
  hpw_label = u"Heure(s) hebdo x 14 semaines"
  coefficient_label = u"Coefficient"
  subjects_label = u"Matière examinée"
  lecture_label = u"Cours"
  recitation_label = u"Exercices"
  project_label = u"Projet"
  labs_label = u"Labo"
  practical_label = u"TP"

  # Make this a set, for quick lookup
  free_text_titles = set([
    u"Préparation pour",
    u"Objectifs d'apprentissage",
    u"Contenu",
    u"Forme d'enseignement",
    u"Forme du contrôle",
    u"Mots clés",
    u"Prérequis",
    u"Bibliographie et matériel",
    u"Remarque",
  ])

  week_hours_re = re.compile(r"(\d+)\s+Heure\(s\) hebdo x (\d+) semaines",
                             flags=re.UNICODE)
  sem_hours_re = re.compile(r"(\d+)\s+Hour\(s\) per semester",
                            flags=re.UNICODE)
  total_hours_re = re.compile(r"(\d+)\s+Heure\(s\)",
                              flags=re.UNICODE)


@caching.CachedJSON(course_desc_path)
def FetchCourseDescriptions(courses):
  descriptions = []

  for course in courses["courses"]:
    description = {
      "study_plan_entry": course,
    }
    for language, url, parser in [("en", course["url"],
                                   ParsedCourseDescription),
                                  ("fr", course["url_fr"],
                                   ParsedCourseDescriptionFrench)]:
      course_desc_html = caching.CachedURLGet(url)
      soup = BeautifulSoup(course_desc_html)
      course_desc = parser(soup)
      try:
        course_desc.ParseDescription()
      except ParsingError as e:
        print "** Parsing error:", e.message
        raise
      description[language] = {
        "title": course_desc.title,
        "instructors": [{ "name": i[0], "url": i[1] }
                        for i in course_desc.instructors],
        "language": course_desc.language,
        "semester": course_desc.semester,
        "credits": course_desc.credits,
        "coefficient": course_desc.coefficient,
        "exam_form": course_desc.exam_form,
        "lecture": course_desc.lecture_hours,
        "recitation": course_desc.recitation_hours,
        "project": course_desc.project_hours,
        "lab": course_desc.lab_hours,
        "practical": course_desc.practical_hours,
        "free_text": dict(course_desc.free_text_desc),
        "links": course_desc.links,
        "library_recommends": course_desc.library_rec,
      }

    descriptions.append(description)

    if course["title"] != description["en"]["title"]:
      print "** Mismatched course titles.",
      print "Section title: '%s'" % course["title"],
      print "Description title: '%s'" % description["en"]["title"]

    print "-- Title:", description["en"]["title"],
    print "/", description["fr"]["title"]
    
    print "-- Instructors:", ", ".join(["%s <%s>" % (i["name"], i["url"])
                                        for i in description["en"]["instructors"]])
    print "-- Language:", description["en"]["language"]

  return {
    "descriptions": descriptions,
  }


def Main():
  logging.basicConfig(level=logging.INFO)

  study_plans = FetchStudyPlans()
  courses = FetchCourseList(study_plans)
  ShowCourseListStatistics(courses)
  
  FetchCourseDescriptions(courses)


if __name__ == "__main__":
  Main()
