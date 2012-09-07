#!/usr/bin/env python
#
# Copyright 2012 EPFL. All rights reserved.

"""Statistics about the consolidated course information."""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import os
import pprint


this_dir = os.path.dirname(__file__)
consolidated_desc_path = os.path.join(this_dir, "consolidated_desc.json")

unique_value_threshold = 100


def AnalyzeOccurrence(cons_data):
  occurrence = {}
  
  for course in cons_data["consolidations"]:
    for language in ["en", "fr"]:
      for key, value in course[language].iteritems():
        if value is None:
          # Ignore unassigned values
          continue
        # Special cases
        if key in ["lecture", "recitation", "project", "practical", "lab"]:
          if "week_hours" in value:
            value = value["week_hours"]
          else:
            continue
        elif isinstance(value, list) or isinstance(value, dict):
          # Skip composite attributes
          continue
        orig_value = occurrence.setdefault(language, {})\
                               .setdefault(key, {})\
                               .setdefault(value, 0)
        occurrence[language][key][value] = orig_value + 1
        
  for lang, lang_name in [("en", "English"), ("fr", "French")]:
    print "-- Statistics for %s" % lang_name
    for key in sorted(occurrence[lang]):
      values = occurrence[lang][key]
      print "- Key '%s' has %d unique values." % (key, len(values))
      if len(values) <= unique_value_threshold:
        print "Value enumeration:"
        pprint.pprint([(k, values[k]) for k in sorted(values.keys())])
    print
    print
        
        


def Main():
  with open(consolidated_desc_path, "r") as f:
    cons_data = json.load(f)
    
  AnalyzeOccurrence(cons_data)


if __name__ == "__main__":
  Main()
