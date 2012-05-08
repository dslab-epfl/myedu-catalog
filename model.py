#
# Copyright notice here
#

"""Models the course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


from google.appengine.ext import db


class Course(db.Model):
  name = db.StringProperty(required=True)
  language = db.StringProperty(required=True, choices=set(["en", "fr"]))
  teachers = db.StringListProperty()
  studies = db.StringListProperty()
  orientations = db.StringListProperty()
  urls = db.StringListProperty()
