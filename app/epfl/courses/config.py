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
    "prop": u"Propédeutique",
    "bachelor": u"Cycle Bachelor",
    "master": u"Cycle Master",
    "edoc": u"Ecole doctorale",
    "min": u"Mineur",
  },
}


EXAM = {
  "en": [
    u'During the semester',
    u'Multiple',
    u'Oral',
    u'Oral presentation',
    u'Project report',
    u'Term paper',
    u'Written',
    u'Written & Oral',
  ],
  "fr": [
    u'Ecrit',
    u'Ecrit & Oral',
    u'Exposé',
    u'Multiple',
    u'Mémoire',
    u'Oral',
    u'Pendant le semestre',
    u'Rapport de TP',
  ],
}

CREDITS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 30]

COEFFICIENT = [ 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0 ]

LECTURE_TIME = [ 1, 2, 3, 4, 6 ]

RECITATION_TIME = [ 1, 2, 3, 4 ]

PROJECT_TIME = [ 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16 ]


SAMPLE_QUERIES = {
  "en": [
    ('section:shs literature OR design',
     'SHS courses on literature or design'),
    ('credits:2 organic materials',
     '2-credit courses related to organic materials'),
    ('semester:fall java',
     'Java-related courses taught in the Fall'),
    ('machine learning credits:4 (codeplan:4 OR codeplan:5)',
     '4-credit MS courses in machine learning'),
    ('section:in (~bio OR ~biology)',
     'Biology-related classes in Computer Science'),
    ('section:sv computer programming',
     'Programming classes for Life Sciences students'),
  ],
  "fr": [
    (u'section:shs littérature OR design',
     u'Cours SHS sur la littérature ou le design'),
    (u'credits:2 matériaux organiques',
     u'Cours à 2 crédits liés aux matériaux organiques'),
    (u'semester:automne java',
     u"Cours de Java et enseigné en automne"),
    (u'machine learning credits:4 (codeplan:4 OR codeplan:5)',
     u"Cours de master à 4 crédits sur l'apprentissage automatique"),
    (u'section:in (~bio OR ~biology)',
     u'Cours de biologie en informatique'),
    (u'section:sv computer programming',
     u'Cours de programmation pour étudiants en Sciences de la Vie'),
  ]
}
