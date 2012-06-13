#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Static data about instructors and courses."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


################################################################################
# Course catalog
################################################################################

# TODO(bucur): Extract this data automatically

RAW_SECTIONS = [
 'AR',
 'AR_ECH',
 'CGC',
 'CGC_CHIM',
 'CGC_ING',
 'EDIC',
 'EDMT',
 'EDNE',
 'EL',
 'EME_MES',
 'ENAC',
 'GC',
 'GM',
 'HPLANS',
 'IF',
 'IN',
 'ING_MATH',
 'ING_PHYS',
 'MA',
 'MATH',
 'MA_CO',
 'MIN_AREA_CULTURAL',
 'MIN_BIOCOMP',
 'MIN_BIOMED',
 'MIN_BIOTECH',
 'MIN_DEV_TER',
 'MIN_ENER',
 'MIN_IN_SEC',
 'MIN_MTE',
 'MIN_TEC_SPACE',
 'MNIS',
 'MT',
 'MTE',
 'MX',
 'PH',
 'PHYS',
 'PH_NE',
 'SC',
 'SC_EPFL',
 'SHS',
 'SIE',
 'SV',
 'SV_B',
 'SV_STV',
 'UNIL_BIU',
 'UNIL_CSU',
 'UNIL_GEU',
 'UNIL_HEC',
 'UNIL_MEU',
 'UNIL_PHU',
 'UNIL_SFU',
]


def _OrganizeSections(sections):
  result_dict = {}
  for section in sections:
    key = section.split("_")[0]
    result_dict.setdefault(key, []).append(section)
    
  return [ [ key ] + result_dict[key] for key in sorted(result_dict.keys()) ]

SECTIONS = _OrganizeSections(RAW_SECTIONS)


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
