#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Static data about instructors and courses."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

################################################################################
# Course catalog
################################################################################

class School(object):
  def __init__(self, code, title_en=None, title_fr=None):
    self.code = code
    self.title_en = title_en
    self.title_fr = title_fr
    
    self.sections = []
    

SCHOOLS = dict([(school.code, school) for school in [
  School("ENAC",
         title_en="Architecture, Civil, and Environmental Engineering"),
  School("IC",
         title_en="Computer and Communication Sciences"),
  School("SB", 
         title_en="Basic Sciences"),
  School("STI",
         title_en="Engineering",
         title_fr=u"Sciences et techniques de l'ingénieur"),
  School("SV",
         title_en="Life Sciences",
         title_fr=u"Sciences de la vie"),
  School("CDH",
         title_en="College of Humanities"),
  School("CDM",
         title_en="Management of Technology"),
  School("EDOC",
         title_en="Doctoral Schools"),
  School("other",
         title_en="Other")
]])


class Section(object):
  def __init__(self, code, school, title_short=None,
               title_en=None, title_fr=None,
               master=False, minor=False):
    self.code = code
    
    self.title_short = title_short
    self.title_en = title_en
    self.title_fr = title_fr
    self.school = school
    self.minor = minor
    self.master = master
    
    SCHOOLS[school].sections.append(self)


SECTIONS = dict([(section.code, section) for section in [
  # ENAC
  Section('AR', 'ENAC', title_short='ENAC-SAR',
          title_en='Architecture'),
  Section('ENAC', 'ENAC', title_short='ENAC',
          title_en='Architecture, Civil, and Environmental Engineering'),
  Section('GC', 'ENAC', title_short='ENAC-SGC',
          title_en='Civil Engineering'),
  Section('MIN-DEV-TER', 'ENAC', title_short='ENAC-DEVTER',
          title_en='Territorial Development',
          minor=True),
  Section('MIN-TEC-SPACE', 'ENAC', title_short='ENAC-TECSPACE',
          title_en='Space Technologies',
          minor=True),
  Section('SIE', 'ENAC', title_short='ENAC-SSIE',
          title_en='Environmental Sciences and Engineering'),

  
  # IC
  Section('IN', 'IC', title_short='IC-SIN',
          title_en='Computer Science'),
  Section('SC', 'IC', title_short='IC-SSC',
          title_en='Communication Systems'),
  Section('SC-EPFL', 'IC', title_short='IC-SSC-MS',
          title_en='Communication Systems',
          master=True),
  Section('MIN-BIOCOMP', 'IC', title_short='IC-BIOCOMP',
          title_en='Biocomputing',
          minor=True),
#  Section('MIN-IN-SEC', 'IC', title_short='IC-INSEC',
#          title_en='Information Security',
#          minor=True),
  
  # SB
  Section('CGC', 'SB', title_short='SB-SCGC',
          title_en='Chemistry and Chemical Engineering'),
  Section('CGC-CHIM', 'SB', title_short='SB-SCGC-CHIM',
          title_en='Molecular and Biological Chemistry'),
  Section('CGC-ING', 'SB', title_short='SB-SCGC-Ing',
          title_en='Chemical Engineering and Biotechnology'),
  Section('ING-MATH', 'SB', title_short='SB-SMA-Ing',
          title_en='Applied Mathematics Sciences'),
  Section('ING-PHYS', 'SB', title_short='SB-SPH-Ing',
          title_en='Applied Physics'),
  Section('MA', 'SB', title_short='SB-SMA',
          title_en='Mathematics'),
  Section('MATH', 'SB', title_short='SB-SMA-MS',
          title_en='Mathematics',
          master=True),
  Section('MA-CO', 'SB', title_short='SB-SMA-CO',
          title_en='Computational Science and Engineering'),
  Section('MIN-BIOMED', 'SB', title_short='SB-BIOMED',
          title_en='Biomedical Technologies',
          minor=True),
  Section('MIN-ENER', 'SB', title_short='SB-ENER',
          title_en='Energy',
          minor=True),
  Section('PH', 'SB', title_short='SB-SPH',
          title_en='Physics'),
  Section('PHYS', 'SB', title_short='SB-SPH-MS',
          title_en='Physics',
          master=True),
  Section('PH-NE', 'SB', title_short='SB-SPH-NE',
          title_en='Nuclear Engineering'),
 
  # STI
  Section('EL', 'STI', title_short='STI-SEL',
          title_en='Electrical and Electronics Engineering'),
  Section('GM', 'STI', title_short='STI-SGM',
          title_en='Mechanical Engineering'),
  Section('MNIS', 'STI', title_short='STI-MNIS',
          title_en='Micro and Nanotechnologies for Integrated Systems'),
  Section('MT', 'STI', title_short='STI-SMT',
          title_en='Microengineering'),
  Section('MX', 'STI', title_short='STI-SMX',
          title_en='Materials Science and Engineering'),
  
  # SV
  Section('MIN-BIOTECH', 'SV', title_short='SV-BIOTECH',
          title_en='Biotechnology',
          minor=True),
  Section('MIN-NEUPRO', 'SV', title_short='SV-NEUPRO',
          title_en=u'Neuroprosthétiques',
          minor=True),
  Section('MIN-NEUR-COMP', 'SV', title_short="SV-NEURCOMP",
          title_en="Neurosciences Computationnelles",
          minor=True),
  Section('SV', 'SV', title_short='SV-SSV',
          title_en='Life Sciences and Technologies'),
  Section('SV-B', 'SV', title_short='SV-SSV-Bio',
          title_en='Bioengineering'),
  Section('SV-STV', 'SV', title_short='SV-SSV-STV',
          title_en='Life Sciences and Technologies',
          master=True),
  
  # CDH
  Section('MIN-AREA-CULTURAL', 'CDH', title_short='CDH-AREACULTURAL',
          title_en='Area and Cultural Studies',
          minor=True),
  Section('SHS', 'CDH', title_short='CDH-SHS',
          title_en='Humanities and Social Sciences'),
  
  # CDM
  Section('IF', 'CDM', title_short='CDM-IF',
          title_en='Financial Engineering'),
  Section('MIN-MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology and Entrepreneurship',
          minor=True),
  Section('MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology and Entrepreneurship'),
                                                         
  # EDOC
  Section('EDAR', 'EDOC', title_short='EDAR',
          title_en='Architecture and Sciences of the City'),
  Section('EDBB', 'EDOC', title_short='EDBB',
          title_en='Biotechnology and Bioengineering'),
  Section('EDCH', 'EDOC', title_short='EDCH',
          title_en='Chemistry and Chemical Engineering'),
  Section('EDCE', 'EDOC', title_short='EDCE',
          title_en='Civil and Environmental Engineering'),
  Section('EDIC', 'EDOC', title_short='EDIC',
          title_en='Computer, Communication and Information Sciences'),
  Section('EDEE', 'EDOC', title_short='EDEE',
          title_en='Electrical Engineering'),
  Section('EDEY', 'EDOC', title_short='EDEY',
          title_en='Energy'),
  Section('EDFI', 'EDOC', title_short='EDFI',
          title_en='Finance'),
  Section('EDMT', 'EDOC', title_short='EDMT',
          title_en='Management of Technology'),
  Section('EDPR', 'EDOC', title_short='EDPR',
          title_en="Manufacturing Systems and Robotics"),
  Section('EDMX', 'EDOC', title_short='EDMX',
          title_en='Materials Science and Engineering'),
  Section('EDMA', 'EDOC', title_short='EDMA',
          title_en="Mathematics"),
  Section('EDME', 'EDOC', title_short='EDME',
          title_en='Mechanics'),
  Section('EDMI', 'EDOC', title_short='EDMI',
          title_en='Microsystems and Microelectronics'),
  Section('EDMS', 'EDOC', title_short='EDMS',
          title_en='Molecular Life Sciences'),                                                                                                         
  Section('EDNE', 'EDOC', title_short='EDNE',
          title_en='Neuroscience'),
  Section('EDPO', 'EDOC', title_short='EDPO',
          title_en='Photonics'),
  Section('EDPY', 'EDOC', title_short='EDPY',
          title_en='Physics'),
 
  # Other
  Section('EME-MES', 'other', title_short='ME-SEME',
          title_en='Energy Management and Sustainability'),
]])


# TODO(bucur): Extract this data automatically.
# This content may become outdated.


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
