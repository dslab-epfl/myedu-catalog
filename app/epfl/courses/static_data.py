#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Static data about instructors and courses."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

# TODO(bucur): Split this in multiple files, so only the necessary data is
# imported.

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
  School("UNIL",
         title_en="University of Lausanne"),
  School("other",
         title_en="Other")
]])


def GetSchool(code, default="other"):
  if code in SCHOOLS:
    return SCHOOLS[code]
  else:
    return SCHOOLS[default]


class Section(object):
  def __init__(self, code, school, title_short=None,
               title_en=None, title_fr=None,
               minor=False, doctoral=False, meta=False):
    self.code = code
    
    self.title_short = title_short
    self.title_en = title_en
    self.title_fr = title_fr
    self.school = school
    self.minor = minor
    self.doctoral = doctoral
    self.meta = meta
    
    SCHOOLS[school].sections.append(self)


SECTIONS = dict([(section.code, section) for section in [
  # ENAC
  Section('AR', 'ENAC', title_short='ENAC-SAR',
          title_en='Architecture'),
  Section('AR_ECH', 'ENAC', title_short='ENAC-SAR-Exch',
          title_en='Architecture Exchange'),
  Section('ENAC', 'ENAC', title_short='ENAC',
          title_en='Architecture, Civil, and Environmental Engineering'),
  Section('GC', 'ENAC', title_short='ENAC-SGC',
          title_en='Civil Engineering'),
  Section('MIN_DEV_TER', 'ENAC', title_short='ENAC-DevTer',
          title_en='Territorial Development', minor=True),
  Section('MIN_TEC_SPACE', 'ENAC', title_short='ENAC-TecSpace',
          title_en='Space Technologies', minor=True),
  Section('SIE', 'ENAC', title_short='ENAC-SSIE',
          title_en='Environmental Sciences and Engineering'),
  
  # IC
  Section('EDIC', 'IC', title_short='EDIC',
          title_en='Computer, Communication and Information Sciences',
          doctoral=True),
  Section('IN', 'IC', title_short='IC-SIN',
          title_en='Computer Science'),
  Section('SC', 'IC', title_short='IC-SSC',
          title_en='Communication Systems / SC'),
  Section('SC_EPFL', 'IC', title_short='IC-SSC-EPFL',
          title_en='Communication Systems / SC_EPFL'),
  Section('MIN_BIOCOMP', 'IC', title_short='IC-BioComp',
          title_en='Biocomputing', minor=True),
  Section('MIN_IN_SEC', 'IC', title_short='IC-InSec',
          title_en='Information Security', minor=True),
  
  # SB
  Section('CGC', 'SB', title_short='SB-SCGC',
          title_en='Chemistry and Chemical Engineering'),
  Section('CGC_CHIM', 'SB', title_short='SB-SCGC-Chim',
          title_en='Molecular and Biological Chemistry'),
  Section('CGC_ING', 'SB', title_short='SB-SCGC-Ing',
          title_en='Chemical Engineering and Biotechnology'),
  Section('ING_MATH', 'SB', title_short='SB-SMA-Ing',
          title_en='Mathematics Engineering'),
  Section('ING_PHYS', 'SB', title_short='SB-SPH-Ing',
          title_en='Physics Engineering'),
  Section('MA', 'SB', title_short='SB-SMA',
          title_en='Mathematics / MA'),
  Section('MATH', 'SB', title_short='SB-SMAth',
          title_en='Mathematics / MATH'),
  Section('MA_CO', 'SB', title_short='SB-SMA-Co',
          title_en='Computational Science and Engineering'),
  Section('MIN_BIOMED', 'SB', title_short='SB-BioMed',
          title_en='Biomedical Technologies', minor=True),
  Section('MIN_ENER', 'SB', title_short='SB-Ener',
          title_en='Energy', minor=True),
  Section('PH', 'SB', title_short='SB-SPH',
          title_en='Physics / PH'),
  Section('PHYS', 'SB', title_short='SB-SPHys',
          title_en='Physics / PHYS'),
  Section('PH_NE', 'SB', title_short='SB-SPH-NE',
          title_en='Nuclear engineering'),
 
  # STI
  Section('EL', 'STI', title_short='STI-SEL',
          title_en='Electrical and Electronics Engineering'),
  Section('EME_MES', 'STI', title_short='STI-SEME',
          title_en='Energy Management and Sustainability'),
  Section('GM', 'STI', title_short='STI-SGM',
          title_en='Mechanical Engineering'),
  Section('MNIS', 'STI', title_short='STI-MNIS',
          title_en='Micro and Nanotechnologies for Integrated Systems'),
  Section('MT', 'STI', title_short='STI-SMT',
          title_en='Microengineering'),
  Section('MX', 'STI', title_short='STI-SMX',
          title_en='Materials Science and Engineering'),
  
  # SV
  Section('EDNE', 'SV', title_short='SV-Neuro',
          title_en='Neuroscience', doctoral=True),
  Section('MIN_BIOTECH', 'SV', title_short='SV-BioTech',
          title_en='Biotechnology', minor=True),
  Section('SV', 'SV', title_short='SV-SSV',
          title_en='Life Sciences and Technologies / SV'),
  Section('SV_B', 'SV', title_short='SV-SSV-Bio',
          title_en='Bioengineering'),
  Section('SV_STV', 'SV', title_short='SV-SSV-STV',
          title_en='Life Sciences and Technologies / SV_STV'),
  
  # CDH
  Section('MIN_AREA_CULTURAL', 'CDH', title_short='CDH-AreaCultural',
          title_en='Area and Cultural Studies', minor=True),
  Section('SHS', 'CDH', title_short='CDH-SHS',
          title_en='Humanities and Social Sciences'),
  
  # CDM  
  Section('EDMT', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology', doctoral=True),
  Section('IF', 'CDM', title_short='CDM-IF',
          title_en='Financial Engineering'),
  Section('MIN_MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology and Entrepreneurship', minor=True),
  Section('MTE', 'CDM', title_short='CDM-MTE',
          title_en='Management of Technology'),
 
  # UNIL
  Section('UNIL_BIU', 'UNIL', title_short='UNIL-BIU',
          title_fr=u'UNIL - Biologie'),
  Section('UNIL_CSU', 'UNIL', title_short='UNIL-CSU',
          title_fr=u'UNIL - Collège des sciences'),
  Section('UNIL_GEU', 'UNIL', title_short='UNIL-GEU',
          title_fr=u'UNIL - Géosciences'),
  Section('UNIL_HEC', 'UNIL', title_short='UNIL-HEC',
          title_fr=u'UNIL - Hautes études commerciales'),
  Section('UNIL_MEU', 'UNIL', title_short='UNIL-MEU',
          title_fr=u'UNIL - Médicine'),
  Section('UNIL_PHU', 'UNIL', title_short='UNIL-PHU',
          title_fr=u'UNIL - Pharmacie'),
  Section('UNIL_SFU', 'UNIL', title_short='UNIL-SFU',
          title_fr=u'UNIL - Sciences forensiques'),
 
  # Other
  Section('HPLANS', 'other',
          title_fr=u'Hors Plans'),
  Section('AUDIT', 'other',
          title_en='Audit', meta=True),
  Section('MINEUR', 'other',
          title_en='Minor', meta=True)
]])


def GetSection(code):
  if code in SECTIONS:
    return SECTIONS[code]
  else:
    return Section(code, SCHOOLS["other"],
                   title_en=code,
                   title_fr=code)


class StudyPlan(object):
  PLANS = {
    "BA": "Bachelor",
    "MA": "Master",
    "PM": "Master project",
  }
  
  SEMESTERS = {
    "E": "Spring",
    "H": "Fall",
    "1": "1st Semester",
    "2": "2nd Semester",
    "3": "3rd Semester",
    "4": "4th Semester",
    "5": "5th Semester",
    "6": "6th Semester"
  }
  
  def __init__(self, code, section=None):
    self.code = code
    parts = self.code.split("-")
    
    self.section = SECTIONS[section] if section else SECTIONS[parts[0]]
    self._plan = None
    self._semester = None
    
    if len(parts) < 2:
      return
    
    if len(parts[1]) == 3:
      self._plan = parts[1][0:2]
      self._semester = parts[1][2]
    elif len(parts[1]) == 1:
      self._semester = parts[1]
    else:
      raise ValueError("Invalid plan syntax")

  @property
  def plan_code(self):
    return self._plan
  
  @property
  def semester_code(self):
    return self._semester
  
  @property
  def plan(self):
    return self.PLANS.get(self._plan)
  
  @property
  def semester(self):
    return self.SEMESTERS.get(self._semester)
  

STUDY_PLANS = dict([(sp.code, sp) for sp in [
  StudyPlan("AR-BA1"),
  StudyPlan("AR-BA2"),
  StudyPlan("AR-BA3"),
  StudyPlan("AR-BA4"),
  StudyPlan("AR-BA5"),
  StudyPlan("AR-BA6"),
  StudyPlan("AR-E"),
  StudyPlan("AR-H"),
  StudyPlan("AR-MA1"),
  StudyPlan("AR-MA2"),
  StudyPlan("AR-MA3"),
  StudyPlan("AR-PME"),
  StudyPlan("AR-PMH"),
  StudyPlan("AUDIT-E"),
  StudyPlan("AUDIT-H"),
  StudyPlan("CGC-BA1"),
  StudyPlan("CGC-BA2"),
  StudyPlan("CGC-BA3"),
  StudyPlan("CGC-BA4"),
  StudyPlan("CGC-BA5"),
  StudyPlan("CGC-BA6"),
  StudyPlan("CGC-MA1"),
  StudyPlan("CGC-MA2"),
  StudyPlan("CGC-MA3"),
  StudyPlan("CGC-PME"),
  StudyPlan("CGC-PMH"),
  StudyPlan("EDIC"),
  StudyPlan("EDMT"),
  StudyPlan("EDNE"),
  StudyPlan("EL-BA1"),
  StudyPlan("EL-BA2"),
  StudyPlan("EL-BA3"),
  StudyPlan("EL-BA4"),
  StudyPlan("EL-BA5"),
  StudyPlan("EL-BA6"),
  StudyPlan("EL-MA1"),
  StudyPlan("EL-MA2"),
  StudyPlan("EL-MA3"),
  StudyPlan("EL-MA4"),
  StudyPlan("EL-PME"),
  StudyPlan("EL-PMH"),
  StudyPlan("EME-MA1", section="EME_MES"),
  StudyPlan("EME-MA2", section="EME_MES"),
  StudyPlan("ENAC-BA4"),
  StudyPlan("ENAC-BA6"),
  StudyPlan("GC-BA1"),
  StudyPlan("GC-BA2"),
  StudyPlan("GC-BA3"),
  StudyPlan("GC-BA4"),
  StudyPlan("GC-BA5"),
  StudyPlan("GC-BA6"),
  StudyPlan("GC-MA1"),
  StudyPlan("GC-MA2"),
  StudyPlan("GC-MA3"),
  StudyPlan("GC-PME"),
  StudyPlan("GC-PMH"),
  StudyPlan("GM-BA1"),
  StudyPlan("GM-BA2"),
  StudyPlan("GM-BA3"),
  StudyPlan("GM-BA4"),
  StudyPlan("GM-BA5"),
  StudyPlan("GM-BA6"),
  StudyPlan("GM-MA1"),
  StudyPlan("GM-MA2"),
  StudyPlan("GM-MA3"),
  StudyPlan("GM-PME"),
  StudyPlan("GM-PMH"),
  StudyPlan("HPLANS-E"),
  StudyPlan("HPLANS-H"),
  StudyPlan("IF-MA1"),
  StudyPlan("IF-MA2"),
  StudyPlan("IF-MA3"),
  StudyPlan("IN-BA1"),
  StudyPlan("IN-BA2"),
  StudyPlan("IN-BA3"),
  StudyPlan("IN-BA4"),
  StudyPlan("IN-BA5"),
  StudyPlan("IN-BA6"),
  StudyPlan("IN-MA1"),
  StudyPlan("IN-MA2"),
  StudyPlan("IN-MA3"),
  StudyPlan("IN-PME"),
  StudyPlan("IN-PMH"),
  StudyPlan("MA-BA1"),
  StudyPlan("MA-BA2"),
  StudyPlan("MA-BA3"),
  StudyPlan("MA-BA4"),
  StudyPlan("MA-BA5"),
  StudyPlan("MA-BA6"),
  StudyPlan("MA-MA1"),
  StudyPlan("MA-MA2"),
  StudyPlan("MA-MA3"),
  StudyPlan("MA-PME"),
  StudyPlan("MA-PMH"),
  StudyPlan("MINEUR-E"),
  StudyPlan("MINEUR-H"),
  StudyPlan("MT-BA1"),
  StudyPlan("MT-BA2"),
  StudyPlan("MT-BA3"),
  StudyPlan("MT-BA4"),
  StudyPlan("MT-BA5"),
  StudyPlan("MT-BA6"),
  StudyPlan("MT-MA1"),
  StudyPlan("MT-MA2"),
  StudyPlan("MT-MA3"),
  StudyPlan("MT-PME"),
  StudyPlan("MT-PMH"),
  StudyPlan("MTE-MA1"),
  StudyPlan("MTE-MA2"),
  StudyPlan("MTE-MA3"),
  StudyPlan("MTE-PME"),
  StudyPlan("MTE-PMH"),
  StudyPlan("MX-BA1"),
  StudyPlan("MX-BA2"),
  StudyPlan("MX-BA3"),
  StudyPlan("MX-BA4"),
  StudyPlan("MX-BA5"),
  StudyPlan("MX-BA6"),
  StudyPlan("MX-MA1"),
  StudyPlan("MX-MA2"),
  StudyPlan("MX-MA3"),
  StudyPlan("MX-PME"),
  StudyPlan("MX-PMH"),
  StudyPlan("PH-BA1"),
  StudyPlan("PH-BA2"),
  StudyPlan("PH-BA3"),
  StudyPlan("PH-BA4"),
  StudyPlan("PH-BA5"),
  StudyPlan("PH-BA6"),
  StudyPlan("PH-MA1"),
  StudyPlan("PH-MA2"),
  StudyPlan("PH-MA3"),
  StudyPlan("PH-MA4"),
  StudyPlan("PH-PME"),
  StudyPlan("PH-PMH"),
  StudyPlan("SC-BA1"),
  StudyPlan("SC-BA2"),
  StudyPlan("SC-BA3"),
  StudyPlan("SC-BA4"),
  StudyPlan("SC-BA5"),
  StudyPlan("SC-BA6"),
  StudyPlan("SC-MA1"),
  StudyPlan("SC-MA2"),
  StudyPlan("SC-MA3"),
  StudyPlan("SC-MA4"),
  StudyPlan("SC-PME"),
  StudyPlan("SC-PMH"),
  StudyPlan("SHS-BA1"),
  StudyPlan("SHS-BA2"),
  StudyPlan("SHS-BA3"),
  StudyPlan("SHS-BA4"),
  StudyPlan("SHS-BA5"),
  StudyPlan("SHS-BA6"),
  StudyPlan("SHS-MA1"),
  StudyPlan("SHS-MA2"),
  StudyPlan("SIE-BA1"),
  StudyPlan("SIE-BA2"),
  StudyPlan("SIE-BA3"),
  StudyPlan("SIE-BA4"),
  StudyPlan("SIE-BA5"),
  StudyPlan("SIE-BA6"),
  StudyPlan("SIE-MA1"),
  StudyPlan("SIE-MA2"),
  StudyPlan("SIE-MA3"),
  StudyPlan("SIE-PME"),
  StudyPlan("SIE-PMH"),
  StudyPlan("SV-BA1"),
  StudyPlan("SV-BA2"),
  StudyPlan("SV-BA3"),
  StudyPlan("SV-BA4"),
  StudyPlan("SV-BA5"),
  StudyPlan("SV-BA6"),
  StudyPlan("SV-MA1"),
  StudyPlan("SV-MA2"),
  StudyPlan("SV-MA3"),
  StudyPlan("SV-PME"),
  StudyPlan("SV-PMH"),
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


################################################################################
# Course description form data
################################################################################

LANGUAGE_CODE = {
  "en": "English",
  "fr": "French",
}

GRADING_CODE = {
  "sem": u"Throughout semester (contrôle continu)",
  "writ": u"Written (exam period)",
  "oral": u"Oral (exam period)",
  "sem_writ": u"Throughout semester + written (exam period)",
  "sem_oral": u"Throughout semester + oral (exam period)",
}

INSTRUCTORS = [
  ("Anastasia", "Ailamaki", "anastasia.ailamaki@epfl.ch"),
  ("George", "Candea", "george.candea@epfl.ch"),
  ("Giovanni", "De Micheli", "giovanni.demicheli@epfl.ch"),
  ("Pierre", "Dillenbourg", "pierre.dillenbourg@epfl.ch"),
  ("Babak", "Falsafi", "babak.falsafi@epfl.ch"),
  ("Boi", "Faltings", "boi.faltings@epfl.ch"),
  ("Pascal", "Fua", "pascal.fua@epfl.ch"),
  ("Wulfram", "Gerstner", "wulfram.gerstner@epfl.ch"),
  ("Roger", "Hersch", "rd.hersch@epfl.ch"),
  ("Jeffrey", "Huang", "jeffrey.huang@epfl.ch"),
  ("Paolo", "Ienne", "paolo.ienne@epfl.ch"),
  ("Christoph", "Koch", "christoph.koch@epfl.ch"),
  ("Bernard", "Moret", "bernard.moret@epfl.ch"),
  ("Martin", "Odersky", "martin.odersky@epfl.ch"),
  ("Mark", "Pauly", "mark.pauly@epfl.ch"),
  ("Claude", "Petitpierre", "claude.petitpierre@epfl.ch"),
  ("Ronan", "Boulic", "ronan.boulic@epfl.ch"),
  ("Christina", "Fragouli", "christina.fragouli@epfl.ch"),
  ("Dejan", "Kostic", "dejan.kostic@epfl.ch"),
  ("Viktor", "Kuncak", "viktor.kuncak@epfl.ch"),
  ("Pearl", "Pu Faltings", "pearl.pu@epfl.ch"),
  ("Martin", "Rajman", "martin.rajman@epfl.ch"),
  ("Matthias", "Seeger", "matthias.seeger@epfl.ch"),
  ("Philippe", "Janson", "philippe.janson@epfl.ch"),
  ("Christian", "Piguet", "christian.piguet@epfl.ch"),
  ("Eduardo", "Sanchez", "eduardo.sanchez@epfl.ch"),
  ("Manuel", "Acevedo", "manuel.acevedo@epfl.ch"),
  ("René", "Beuchat", "rene.beuchat@epfl.ch"),
  ("Jean-Cédric", "Chappelier", "jean-cedric.chappelier@epfl.ch"),
  ("Jean-Luc", "Desbiolles", "jean-luc.desbiolles@epfl.ch"),
  ("Patrick", "Jermann", "patrick.jermann@epfl.ch"),
  ("Ties", "Kluter", "ties.kluter@epfl.ch"),
  ("Hendrik Ole", "Knoche", "hendrik.knoche@epfl.ch"),
  ("Marc", "Lecoultre", "marc.lecoultre@epfl.ch"),
  ("Vincent", "Lepetit", "vincent.lepetit@epfl.ch"),
  ("Thomas", "Lochmatter", "thomas.lochmatter@epfl.ch"),
  ("Jean-Philippe", "Pellet", "jean-philippe.pellet@epfl.ch"),
  ("Pierre-Yves", "Rochat", "pierre-yves.rochat@epfl.ch"),
  ("Jamila", "Sam", "jamila.sam@epfl.ch"),
  ("Michel", "Schinz", "michel.schinz@epfl.ch")
]

INSTRUCTORS_NEW = [
  ("Alain", "Wegmann"),
  ("Aleksander", "Madry"),
  ("Amin", "Shokrollahi"),
  ("Amina", "Chebira"),
  ("Anastasia", "Ailamaki"),
  ("Andrea", "Ridolfi"),
  ("André", "Schiper"),
  ("Arjen", "Lenstra"),
  ("Babak", "Falsafi"),
  ("Bernard", "Moret"),
  ("Bertrand", "Dutoit"),
  ("Bixio", "Rimoldi"),
  ("Boi", "Faltings"),
  ("Catherine", "Monnin"),
  ("Christian", "Piguet"),
  ("Christina", "Fragouli"),
  ("Christine", "Vanoirbeek"),
  ("Christof", "Faller"),
  ("Christoph", "Koch"),
  ("Claude", "Petitpierre"),
  ("Dejan", "Kostic"),
  ("Eduardo", "Sanchez"),
  ("Emre", "Telatar"),
  ("Eytan", "Zysman"),
  ("Friedrich", "Eisenbrand"),
  ("George", "Candea"),
  ("Giovanni", "De Micheli"),
  ("Gregor", "Rainer"),
  ("Hendrik Ole", "Knoche"),
  ("Hubert", "Kirrmann"),
  ("Jamila", "Sam"),
  ("Jean-Cédric", "Chappelier"),
  ("Jean-Dominique", "Decotignie"),
  ("Jean-Luc", "Desbiolles"),
  ("Jean-Philippe", "Pellet"),
  ("Jean-Pierre", "Hubaux"),
  ("Jean-Yves", "Le Boudec"),
  ("Jeffrey", "Huang"),
  ("Joseph", "Sifakis"),
  ("Karl", "Aberer"),
  ("Katerina", "Argyraki"),
  ("Manuel", "Acevedo"),
  ("Marc", "Lecoultre"),
  ("Mark", "Pauly"),
  ("Martin", "Odersky"),
  ("Martin", "Rajman"),
  ("Martin", "Vetterli"),
  ("Matthias", "Grossglauser"),
  ("Matthias", "Seeger"),
  ("Michael", "Gastpar"),
  ("Olivier", "Lévêque"),
  ("Paolo", "Ienne"),
  ("Pascal", "Fua"),
  ("Patrick", "Jermann"),
  ("Patrick", "Thiran"),
  ("Pearl", "Pu Faltings"),
  ("Philippe", "Oechslin"),
  ("Philippe", "Janson"),
  ("Pierre", "Dillenbourg"),
  ("Pierre-Yves", "Rochat"),
  ("Rachid", "Guerraoui"),
  ("René", "Beuchat"),
  ("Roger", "Hersch"),
  ("Ronan", "Boulic"),
  ("Rüdiger", "Urbanke"),
  ("Sabine", "Süsstrunk"),
  ("Schinz", "Michel"),
  ("Serge", "Vaudenay"),
  ("Thomas", "Heinis"),
  ("Thomas", "Lochmatter"),
  ("Ties", "Kluter"),
  ("Viktor", "Kuncak"),
  ("Vincent", "Lepetit"),
  ("Willy", "Zwaenepoel"),
  ("Wulfram", "Gerstner"),
  ("Xiuwei", "Zhang"),
]

PREREQUISITES = [
  ("CS-100", "Introduction aux systèmes informatiques"),
  ("CS-105", "Introduction à la programmation objet"),
  ("CS-106", "Théorie et pratique de la programmation"),
  ("CS-150", "Discrete structures"),
  ("CS-170", "Systèmes logiques  I"),
  ("CS-172", "Systèmes logiques  II"),
  ("CS-198", "Projet de technologie de l'information"),
  ("CS-205", "Programmation avancée"),
  ("CS-206", "Concurrence"),
  ("CS-207", "Programmation orientée système"),
  ("CS-250", "Algorithms"),
  ("CS-251", "Informatique théorique"),
  ("CS-252", "Advanced theoretical computer sciences"),
  ("CS-270", "Architecture des ordinateurs I"),
  ("CS-271", "Architecture des ordinateurs II"),
  ("CS-305", "Software engineering"),
  ("CS-306", "Software development project"),
  ("CS-320", "Compiler construction"),
  ("CS-321", "Informatique du temps réel"),
  ("CS-322", "Introduction to database systems"),
  ("CS-323", "Operating systems"),
  ("CS-330", "Intelligence artificielle"),
  ("CS-341", "Introduction to computer graphics"),
  ("CS-350", "Graph theory applications"),
  ("CS-370", "Introduction to Multiprocessor Architecture"),
  ("CS-398", "Projet en Informatique I"),
  ("COM-101", "Sciences de l'information"),
  ("COM-203", "Digital photography"),
  ("COM-208", "Computer networks"),
  ("COM-300", "Modèles stochastiques pour les communications"),
  ("COM-301", "Sécurité des réseaux"),
  ("COM-302", "Principles of digital communications"),
  ("COM-303", "Signal processing for communications"),
  ("COM-307", "Projet en systemes de communication I"),
  ("EE-204", "Circuits and systems I"),
  ("EE-205", "Circuits and systems II"),
  ("MATH-103", "Analyse I"),
  ("MATH-107", "Analyse II"),
  ("MATH-111b", "Algèbre linéaire"),
  ("MATH-203c", "Analyse III"),
  ("MATH-207b", "Analyse IV"),
  ("MATH-232", "Probabilités et statistiques")
]
