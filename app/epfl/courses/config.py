#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""MyEdu configuration options."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import datetime


# The size of a results page
PAGE_SIZE = 20

# The official launch date of the application
LAUNCH_DATE = datetime.datetime(2012, 6, 14, 17, 20)

# The Google Custom Search ID
SEARCH_ENGINE_ID = "000528554756935640955:t5p6oxkfane"


STUDY_PLANS = {
  "en": {
    "prop": "Propedeutics",
    "bachelor": "Bachelor",
    "master": "Master",
    "edoc": "Doctoral",
    "min": "Minor",
  },
  "fr": {
    "prop": "Propedeutics",
    "bachelor": "Bachelor",
    "master": "Master",
    "edoc": "Doctoral",
    "min": "Minor",
  },
}

EXAM = [
  "During the semester",
  "Oral",
  "Term paper",
  "Written"
]

CREDITS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 20, 30]

COEFFICIENT = [ 0.5, 1.0, 1.5, 2.0, 3.0, 4.0 ]

LECTURE_TIME = [ 1, 2, 3, 4, 5, 6 ]

RECITATION_TIME = [ 1, 2, 3, 4 ]

PROJECT_TIME = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16 ]

SAMPLE_QUERIES = [
  ('plan:"SHS-BA3" literature OR design',
   'SHS courses on literature or design, taught in the 3rd bachelor semester'),
  ('credits:2 "organic materials"',
   '2-credit courses on organic materials'),
  ('semester:fall java',
   'Java-related courses taught in the Fall'),
  ('section:"MIN-IN-SEC" -cryptography',
   'Courses in the computer security minor that do not teach cryptography'),
]