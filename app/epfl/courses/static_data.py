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
  def __init__(self, code, school, title_en=None, title_fr=None,
               minor=False, doctoral=False):
    self.code = code
    
    self.title_en = title_en
    self.title_fr = title_fr
    self.school = school
    self.minor = minor
    self.doctoral = doctoral
    
    SCHOOLS[school].sections.append(self)


SECTIONS = dict([(section.code, section) for section in [
  # ENAC
  Section('AR', 'ENAC',
          title_en='Architecture'),
  Section('AR_ECH', 'ENAC',
          title_en='Architecture Exchange'),
  Section('ENAC', 'ENAC',
          title_en='Architecture, Civil, and Environmental Engineering'),
  Section('GC', 'ENAC',
          title_en='Civil Engineering'),
  Section('MIN_DEV_TER', 'ENAC',
          title_en='Territorial Development', minor=True),
  Section('MIN_TEC_SPACE', 'ENAC',
          title_en='Space Technologies', minor=True),
  Section('SIE', 'ENAC',
          title_en='Environmental Sciences and Engineering'),
  
  # IC
  Section('EDIC', 'IC',
          title_en='Computer, Communication and Information Sciences',
          doctoral=True),
  Section('IN', 'IC',
          title_en='Computer Science'),
  Section('SC', 'IC',
          title_en='Communication Systems (SC)'),
  Section('SC_EPFL', 'IC',
          title_en='Communication Systems (SC_EPFL)'),
  Section('MIN_BIOCOMP', 'IC',
          title_en='Biocomputing', minor=True),
  Section('MIN_IN_SEC', 'IC',
          title_en='Information Security', minor=True),
  
  # SB
  Section('CGC', 'SB',
          title_en='Chemistry and Chemical Engineering'),
  Section('CGC_CHIM', 'SB',
          title_en='Molecular and Biological Chemistry'),
  Section('CGC_ING', 'SB',
          title_en='Chemical Engineering and Biotechnology'),
  Section('ING_MATH', 'SB',
          title_en='Mathematics Engineering'),
  Section('ING_PHYS', 'SB',
          title_en='Physics Engineering'),
  Section('MA', 'SB',
          title_en='Mathematics (MA)'),
  Section('MATH', 'SB',
          title_en='Mathematics (MA_CO)'),
  Section('MA_CO', 'SB',
          title_en='Computational Science and Engineering'),
  Section('MIN_BIOMED', 'SB',
          title_en='Biomedical Technologies', minor=True),
  Section('MIN_ENER', 'SB',
          title_en='Energy', minor=True),
  Section('PH', 'SB',
          title_en='Physics (PH)'),
  Section('PHYS', 'SB',
          title_en='Physics (PHYS)'),
  Section('PH_NE', 'SB',
          title_en='Nuclear engineering'),
 
  # STI
  Section('EL', 'STI',
          title_en='Electrical and Electronics Engineering'),
  Section('EME', 'STI',
          title_en='Energy Management and Sustainability (EME)'),
  Section('EME_MES', 'STI',
          title_en='Energy Management and Sustainability (EME_MES)'),
  Section('GM', 'STI',
          title_en='Mechanical Engineering'),
  Section('MNIS', 'STI',
          title_en='Micro and Nanotechnologies for Integrated Systems'),
  Section('MT', 'STI',
          title_en='Microengineering'),
  Section('MX', 'STI',
          title_en='Materials Science and Engineering'),
  
  # SV
  Section('EDNE', 'SV',
          title_en='Neuroscience', doctoral=True),
  Section('MIN_BIOTECH', 'SV',
          title_en='Biotechnology', minor=True),
  Section('SV', 'SV',
          title_en='Life Sciences and Technologies (SV)'),
  Section('SV_B', 'SV',
          title_en='Bioengineering'),
  Section('SV_STV', 'SV',
          title_en='Life Sciences and Technologies (SV_STV)'),
  
  # CDH
  Section('MIN_AREA_CULTURAL', 'CDH',
          title_en='Area and Cultural Studies', minor=True),
  Section('SHS', 'CDH',
          title_en='Humanities and Social Sciences'),
  
  # CDM  
  Section('EDMT', 'CDM',
          title_en='Management of Technology', doctoral=True),
  Section('IF', 'CDM',
          title_en='Financial Engineering'),
  Section('MIN_MTE', 'CDM',
          title_en='Management of Technology and Entrepreneurship', minor=True),
  Section('MTE', 'CDM',
          title_en='Management of Technology'),
 
  # UNIL
  Section('UNIL_BIU', 'UNIL',
          title_fr=u'UNIL - Biologie'),
  Section('UNIL_CSU', 'UNIL',
          title_fr=u'UNIL - Collège des sciences'),
  Section('UNIL_GEU', 'UNIL',
          title_fr=u'UNIL - Géosciences'),
  Section('UNIL_HEC', 'UNIL',
          title_fr=u'UNIL - Hautes études commerciales'),
  Section('UNIL_MEU', 'UNIL',
          title_fr=u'UNIL - Médicine'),
  Section('UNIL_PHU', 'UNIL',
          title_fr=u'UNIL - Pharmacie'),
  Section('UNIL_SFU', 'UNIL',
          title_fr=u'UNIL - Sciences forensiques'),
 
  # Other
  Section('HPLANS', 'other',
          title_fr=u'Hors Plans'),
  Section('AUDIT', 'other',
          title_en='Audit'),
  Section('MINEUR', 'other',
          title_en='Minor')
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
  
  def __init__(self, code):
    self.code = code
    parts = self.code.split("-")
    
    self.section = SECTIONS[parts[0]]
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
  

STUDY_PLANS = dict([(sp.code, sp) for sp in [StudyPlan(code) for code in [
  "AR-BA1",
  "AR-BA2",
  "AR-BA3",
  "AR-BA4",
  "AR-BA5",
  "AR-BA6",
  "AR-E",
  "AR-H",
  "AR-MA1",
  "AR-MA2",
  "AR-MA3",
  "AR-PME",
  "AR-PMH",
  "AUDIT-E",
  "AUDIT-H",
  "CGC-BA1",
  "CGC-BA2",
  "CGC-BA3",
  "CGC-BA4",
  "CGC-BA5",
  "CGC-BA6",
  "CGC-MA1",
  "CGC-MA2",
  "CGC-MA3",
  "CGC-PME",
  "CGC-PMH",
  "EDIC",
  "EDMT",
  "EDNE",
  "EL-BA1",
  "EL-BA2",
  "EL-BA3",
  "EL-BA4",
  "EL-BA5",
  "EL-BA6",
  "EL-MA1",
  "EL-MA2",
  "EL-MA3",
  "EL-MA4",
  "EL-PME",
  "EL-PMH",
  "EME-MA1",
  "EME-MA2",
  "ENAC-BA4",
  "ENAC-BA6",
  "GC-BA1",
  "GC-BA2",
  "GC-BA3",
  "GC-BA4",
  "GC-BA5",
  "GC-BA6",
  "GC-MA1",
  "GC-MA2",
  "GC-MA3",
  "GC-PME",
  "GC-PMH",
  "GM-BA1",
  "GM-BA2",
  "GM-BA3",
  "GM-BA4",
  "GM-BA5",
  "GM-BA6",
  "GM-MA1",
  "GM-MA2",
  "GM-MA3",
  "GM-PME",
  "GM-PMH",
  "HPLANS-E",
  "HPLANS-H",
  "IF-MA1",
  "IF-MA2",
  "IF-MA3",
  "IN-BA1",
  "IN-BA2",
  "IN-BA3",
  "IN-BA4",
  "IN-BA5",
  "IN-BA6",
  "IN-MA1",
  "IN-MA2",
  "IN-MA3",
  "IN-PME",
  "IN-PMH",
  "MA-BA1",
  "MA-BA2",
  "MA-BA3",
  "MA-BA4",
  "MA-BA5",
  "MA-BA6",
  "MA-MA1",
  "MA-MA2",
  "MA-MA3",
  "MA-PME",
  "MA-PMH",
  "MINEUR-E",
  "MINEUR-H",
  "MT-BA1",
  "MT-BA2",
  "MT-BA3",
  "MT-BA4",
  "MT-BA5",
  "MT-BA6",
  "MT-MA1",
  "MT-MA2",
  "MT-MA3",
  "MT-PME",
  "MT-PMH",
  "MTE-MA1",
  "MTE-MA2",
  "MTE-MA3",
  "MTE-PME",
  "MTE-PMH",
  "MX-BA1",
  "MX-BA2",
  "MX-BA3",
  "MX-BA4",
  "MX-BA5",
  "MX-BA6",
  "MX-MA1",
  "MX-MA2",
  "MX-MA3",
  "MX-PME",
  "MX-PMH",
  "PH-BA1",
  "PH-BA2",
  "PH-BA3",
  "PH-BA4",
  "PH-BA5",
  "PH-BA6",
  "PH-MA1",
  "PH-MA2",
  "PH-MA3",
  "PH-MA4",
  "PH-PME",
  "PH-PMH",
  "SC-BA1",
  "SC-BA2",
  "SC-BA3",
  "SC-BA4",
  "SC-BA5",
  "SC-BA6",
  "SC-MA1",
  "SC-MA2",
  "SC-MA3",
  "SC-MA4",
  "SC-PME",
  "SC-PMH",
  "SHS-BA1",
  "SHS-BA2",
  "SHS-BA3",
  "SHS-BA4",
  "SHS-BA5",
  "SHS-BA6",
  "SHS-MA1",
  "SHS-MA2",
  "SIE-BA1",
  "SIE-BA2",
  "SIE-BA3",
  "SIE-BA4",
  "SIE-BA5",
  "SIE-BA6",
  "SIE-MA1",
  "SIE-MA2",
  "SIE-MA3",
  "SIE-PME",
  "SIE-PMH",
  "SV-BA1",
  "SV-BA2",
  "SV-BA3",
  "SV-BA4",
  "SV-BA5",
  "SV-BA6",
  "SV-MA1",
  "SV-MA2",
  "SV-MA3",
  "SV-PME",
  "SV-PMH"
]]])


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
