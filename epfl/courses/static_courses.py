#!/usr/bin/env python
# -*- coding: utf-8 -*-

INSTRUCTORS = [
  ("Anastasia", "Ailamaki", "anastasia.ailamaki@epfl.ch"),
  ("George", "Candea", "george.candea@epfl.ch"),
  ("Giovanni", "de Micheli", "giovanni.demicheli@epfl.ch"),
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
  ("Karl", "Aberer"),
  ("Manuel", "Acevedo"),
  ("Anastasia", "Ailamaki"),
  ("Katerina", "Argyraki"),
  ("René", "Beuchat"),
  ("Ronan", "Boulic"),
  ("George", "Candea"),
  ("Jean-Cédric", "Chappelier"),
  ("Giovanni", "de Micheli"),
  ("Jean-Dominique", "Decotignie"), 
  ("Jean-Luc", "Desbiolles"),
  ("Pierre", "Dillenbourg"),
  ("Friedrich", "Eisenbrand"),
  ("Babak", "Falsafi"),
  ("Boi", "Faltings"),
  ("Christina", "Fragouli"), 
  ("Pascal", "Fua"),
  ("Michael", "Gastpar"), 
  ("Wulfram", "Gerstner"),
  ("Matthias", "Grossglauser"),
  ("Rachid", "Guerraoui"),
  ("Roger", "Hersch"),
  ("Jeffrey", "Huang"),
  ("Jean-Pierre", "Hubaux"),
  ("Paolo", "Ienne"),
  ("Philippe", "Janson"),
  ("Patrick", "Jermann"),
  ("Ties", "Kluter"),
  ("Hendrik Ole", "Knoche"),
  ("Christoph", "Koch"),
  ("Dejan", "Kostic"),
  ("Viktor", "Kuncak"),
  ("Jean-Yves", "Le Boudec"),
  ("Marc", "Lecoultre"),
  ("Arjen", "Lenstra"),
  ("Vincent", "Lepetit"),
  ("Thomas", "Lochmatter"),
  ("Aleksander", "Madry"),
  ("Schinz", "Michel"),
  ("Bernard", "Moret"),
  ("Martin", "Odersky"),
  ("Mark", "Pauly"),
  ("Pearl", "Pu Faltings"),
  ("Jean-Philippe", "Pellet"),
  ("Claude", "Petitpierre"),
  ("Christian", "Piguet"),
  ("Gregor", "Rainer"),
  ("Martin", "Rajman"),
  ("Bixio", "Rimoldi"),
  ("Pierre-Yves", "Rochat"),
  ("Jamila", "Sam"),
  ("Eduardo", "Sanchez"),
  ("André", "Schiper"),
  ("Matthias", "Seeger"),
  ("Amin", "Shokrollahi"),
  ("Sabine", "Süsstrunk"),
  ("Emre", "Telatar"),
  ("Patrick", "Thiran"),
  ("Rüdiger", "Urbanke"),
  ("Serge", "Vaudenay"),
  ("Martin", "Vetterli"),
  ("Alain", "Wegmann"),
  ("Willy", "Zwaenepoel"), 
]

PREREQUISITES = [
  ("CS-100", "Introduction aux systèmes informatiques"),
  ("CS-105", "Introduction à la programmation objet"),
  ("CS-106", "Théorie et pratique de la programmation"),
  ("CS-150", "Discrete structures"),
  ("CS-170", "Systèmes logiques  I"),
  ("CS-172", "Systèmes logiques  II"),
  ("CS-198", "Projet de technologie (de l'information)"),
  ("CS-205", "Programmation avancée"),
  ("CS-206", "Concurrence"),
  ("CS-207", "Programmation orientée système"),
  ("CS-250", "Algorithms"),
  ("CS-251", "Informatique théorique"),
  ("CS-252", "Advanced theoretical computer sciences"),
  ("CS-270", "Architecture des ordinateurs I"),
  ("CS-271", "Architecture des ordinateurs II"),
  ("CS-305", "Software engineering"),
  ("CS-306", "Software development (project)"),
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
