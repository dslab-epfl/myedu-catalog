#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Static data used to populate the datastore."""

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
         title_en="Architecture, Civil, and Environmental Engineering",
         title_fr=u"Environnement naturel, architectural et construit"),
  School("IC",
         title_en="Computer and Communication Sciences",
         title_fr=u"Informatique et communications"),
  School("SB", 
         title_en="Basic Sciences",
         title_fr=u"Sciences de base"),
  School("STI",
         title_en="Engineering",
         title_fr=u"Sciences et techniques de l'ingénieur"),
  School("SV",
         title_en="Life Sciences",
         title_fr=u"Sciences de la vie"),
  School("CDH",
         title_en="College of Humanities",
         title_fr=u"Collège des humanités"),
  School("CDM",
         title_en="Management of Technology",
         title_fr=u"Collège du management de la technologie"),
  School("EDOC",
         title_en="Doctoral Schools",
         title_fr=u"Ecole doctorale"),
  School("other",
         title_en="Other",
         title_fr=u"Autre")
]])


class Section(object):
  def __init__(self, code, school, title_short=None,
               title_en=None, title_fr=None,
               master=False, minor=False,
               alias=None):
    self.code = code
    
    self.title_short = title_short
    self.title_en = title_en
    self.title_fr = title_fr
    self.school = school
    self.minor = minor
    self.master = master
    self.alias = alias
    
    SCHOOLS[school].sections.append(self)


SECTIONS = dict([(section.code, section) for section in [
  # ENAC
  Section('AR', 'ENAC', title_short='ENAC-SAR',
          title_en='Architecture',
          title_fr=u'Architecture'),
  Section('ENAC', 'ENAC', title_short='ENAC',
          title_en='Architecture, Civil, and Environmental Engineering',
          title_fr=u'Environnement naturel, architectural et construit'),
  Section('GC', 'ENAC', title_short='ENAC-SGC',
          title_en='Civil Engineering',
          title_fr=u'Génie civil'),
  Section('MIN-DEV-TER', 'ENAC', title_short='ENAC-DEVTER',
          title_en='Territorial Development',
          title_fr=u'Développement territorial et urbanisme',
          minor=True),
  Section('MIN-TEC-SPACE', 'ENAC', title_short='ENAC-TECSPACE',
          title_en='Space Technologies',
          title_fr=u'Technologies spatiales',
          minor=True),
  Section('SIE', 'ENAC', title_short='ENAC-SSIE',
          title_en='Environmental Sciences and Engineering',
          title_fr=u"Sciences et ingénierie de l'environnement"),
  
  # IC
  Section('IN', 'IC', title_short='IC-SIN',
          title_en='Computer Science',
          title_fr=u'Informatique'),
  Section('SC', 'IC', title_short='IC-SSC',
          title_en='Communication Systems',
          title_fr=u'Systèmes de communication'),
  Section('SC-EPFL', 'IC', title_short='IC-SSC-MS',
          title_en='Communication Systems',
          title_fr=u'Systèmes de communication',
          alias='SC'),
  Section('MIN-BIOCOMP', 'IC', title_short='IC-BIOCOMP',
          title_en='Biocomputing',
          title_fr=u'Biocomputing',
          minor=True),
  
  # SB
  Section('CGC', 'SB', title_short='SB-SCGC',
          title_en='Chemistry and Chemical Engineering',
          title_fr=u'Chimie et génie chimique'),
  Section('CGC-CHIM', 'SB', title_short='SB-SCGC-CHIM',
          title_en='Molecular and Biological Chemistry',
          title_fr=u'Chimie moléculaire et biologique'),
  Section('CGC-ING', 'SB', title_short='SB-SCGC-Ing',
          title_en='Chemical Engineering and Biotechnology',
          title_fr=u'Génie chimique et Biotechnologie'),
  Section('ING-MATH', 'SB', title_short='SB-SMA-Ing',
          title_en='Applied Mathematics Sciences',
          title_fr=u'Ingénierie mathématique'),
  Section('ING-PHYS', 'SB', title_short='SB-SPH-Ing',
          title_en='Applied Physics',
          title_fr=u'Ingénierie physique'),
  Section('MA', 'SB', title_short='SB-SMA',
          title_en='Mathematics',
          title_fr=u'Mathématiques'),
  Section('MATH', 'SB', title_short='SB-SMA-MS',
          title_en='Mathematics',
          title_fr=u'Mathématiques',
          alias='MA'),
  Section('MA-CO', 'SB', title_short='SB-SMA-CO',
          title_en='Computational Science and Engineering',
          title_fr=u'Science et ingénierie computationnelles'),
  Section('MIN-BIOMED', 'SB', title_short='SB-BIOMED',
          title_en='Biomedical Technologies',
          title_fr=u'Technologies biomédicales',
          minor=True),
  Section('MIN-ENER', 'SB', title_short='SB-ENER',
          title_en='Energy',
          title_fr=u'Énergie',
          minor=True),
  Section('PH', 'SB', title_short='SB-SPH',
          title_en='Physics',
          title_fr=u'Physique'),
  Section('PHYS', 'SB', title_short='SB-SPH-MS',
          title_en='Physics',
          title_fr=u'Physique',
          alias='PHYS'),
  Section('PH-NE', 'SB', title_short='SB-SPH-NE',
          title_en='Nuclear Engineering',
          title_fr=u'Génie nucléaire'),
 
  # STI
  Section('EL', 'STI', title_short='STI-SEL',
          title_en='Electrical and Electronics Engineering',
          title_fr=u'Génie électrique et électronique'),
  Section('GM', 'STI', title_short='STI-SGM',
          title_en='Mechanical Engineering',
          title_fr=u'Génie mécanique'),
  Section('MNIS', 'STI', title_short='STI-MNIS',
          title_en='Micro and Nanotechnologies for Integrated Systems',
          title_fr=u'Micro and Nanotechnologies for Integrated Systems'),
  Section('MT', 'STI', title_short='STI-SMT',
          title_en='Microengineering',
          title_fr=u'Microtechnique'),
  Section('MX', 'STI', title_short='STI-SMX',
          title_en='Materials Science and Engineering',
          title_fr=u'Science et génie des matériaux'),
  
  # SV
  Section('MIN-BIOTECH', 'SV', title_short='SV-BIOTECH',
          title_en='Biotechnology',
          title_fr=u'Biotechnologie',
          minor=True),
  Section('MIN-NEUPRO', 'SV', title_short='SV-NEUPRO',
          title_en=u'Neuroprosthétiques',
          title_fr=u'Neuroprosthétiques',
          minor=True),
  Section('MIN-NEUR-COMP', 'SV', title_short="SV-NEURCOMP",
          title_en="Neurosciences Computationnelles",
          title_fr=u'Neurosciences computationnelles',
          minor=True),
  Section('SV', 'SV', title_short='SV-SSV',
          title_en='Life Sciences and Technologies',
          title_fr=u'Sciences et technologies du vivant'),
  Section('SV-B', 'SV', title_short='SV-SSV-Bio',
          title_en='Bioengineering',
          title_fr=u'Bioingénierie'),
  Section('SV-STV', 'SV', title_short='SV-SSV-STV',
          title_en='Life Sciences and Technologies',
          title_fr='Sciences et technologies du vivant',
          alias='SV'),
  
  # CDH
  Section('MIN-AREA-CULTURAL', 'CDH', title_short='CDH-AREACULTURAL',
          title_en='Area and Cultural Studies',
          title_fr=u'Area and Cultural Studies',
          minor=True),
  Section('SHS', 'CDH', title_short='CDH-SHS',
          title_en='Humanities and Social Sciences',
          title_fr=u'Sciences humaines et sociales'),
  
  # CDM
  Section('IF', 'CDM', title_short='CDM-IF',
          title_en='Financial Engineering',
          title_fr=u'Ingénierie financière'),
  Section('MIN-MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology and Entrepreneurship',
          title_fr=u'Management de la technologie et entrepreneuriat',
          minor=True),
  Section('MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology and Entrepreneurship',
          title_fr=u'Management de la technologie et entrepreneuriat'),
  Section('MTEE', 'CDM', title_short='CDM-MTEE',
          title_en='Management of Technology and Entrepreneurship',
          title_fr=u'Management de la technologie et entrepreneuriat',
          alias='MTE'),
                                                         
  # EDOC
  Section('EDAR', 'EDOC', title_short='EDAR',
          title_en='Architecture and Sciences of the City',
          title_fr=u'Architecture et sciences de la ville'),
  Section('EDBB', 'EDOC', title_short='EDBB',
          title_en='Biotechnology and Bioengineering',
          title_fr=u'Biotechnologie et génie biologique'),
  Section('EDCH', 'EDOC', title_short='EDCH',
          title_en='Chemistry and Chemical Engineering',
          title_fr=u'Chimie et génie chimique'),
  Section('EDCE', 'EDOC', title_short='EDCE',
          title_en='Civil and Environmental Engineering',
          title_fr=u'Génie civil et environnement'),
  Section('EDIC', 'EDOC', title_short='EDIC',
          title_en='Computer, Communication and Information Sciences',
          title_fr=u'Informatique, communications et information'),
  Section('EDEE', 'EDOC', title_short='EDEE',
          title_en='Electrical Engineering',
          title_fr=u'Génie électrique'),
  Section('EDEY', 'EDOC', title_short='EDEY',
          title_en='Energy',
          title_fr=u'Energie'),
  Section('EDFI', 'EDOC', title_short='EDFI',
          title_en='Finance',
          title_fr=u'Finance'),
  Section('EDMT', 'EDOC', title_short='EDMT',
          title_en='Management of Technology',
          title_fr=u'Management de la technologie'),
  Section('EDPR', 'EDOC', title_short='EDPR',
          title_en="Manufacturing Systems and Robotics",
          title_fr=u'Systèmes de production et robotique'),
  Section('EDMX', 'EDOC', title_short='EDMX',
          title_en='Materials Science and Engineering',
          title_fr=u'Science et génie des matériaux'),
  Section('EDMA', 'EDOC', title_short='EDMA',
          title_en="Mathematics",
          title_fr=u"Mathématiques"),
  Section('EDME', 'EDOC', title_short='EDME',
          title_en='Mechanics',
          title_fr=u'Mécanique'),
  Section('EDMI', 'EDOC', title_short='EDMI',
          title_en='Microsystems and Microelectronics',
          title_fr=u'Microsystèmes et microélectronique'),
  Section('EDMS', 'EDOC', title_short='EDMS',
          title_en='Molecular Life Sciences',
          title_fr=u'Approches moléculaires du vivant'),                                                                                                         
  Section('EDNE', 'EDOC', title_short='EDNE',
          title_en='Neuroscience',
          title_fr=u'Neurosciences'),
  Section('EDPO', 'EDOC', title_short='EDPO',
          title_en='Photonics',
          title_fr=u'Photonique'),
  Section('EDPY', 'EDOC', title_short='EDPY',
          title_en='Physics',
          title_fr=u'Physique'),
 
  # Other
  Section('EME-MES', 'other', title_short='ME-SEME',
          title_en='Energy Management and Sustainability',
          title_fr=u"Gestion de l'énergie et construction durable"),
]])
