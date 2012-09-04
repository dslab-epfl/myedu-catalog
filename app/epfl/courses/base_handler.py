#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""Common request handler functionality (authentication, user info, etc.)"""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import re
import unicodedata
import webapp2

from webapp2_extras import jinja2


class BaseHandler(webapp2.RequestHandler):
  """Base handler that contains various common utilities."""
  
  _isa_replacement_map = {
    "[/b]": "</b>", 
    "[/i]": "</i>", 
    "[b]": "<b>", 
    "[br/]": "<br/>", 
    "[br]": "<br/>", 
    "[i]": "<i>", 
    "[li]": u"•  ",
  }
  
  @webapp2.cached_property
  def jinja2(self):
    """The Jinja object."""
    
    return jinja2.get_jinja2(app=self.app)
  
  def RenderTemplate(self, filename, template_args):
    """Render a template to the response output stream."""
    
    self.response.write(self.jinja2.render_template(filename, **template_args))
    
  def GetRenderedTemplate(self, filename, template_args):
    """Return a rendered template, without writing in the response."""
    
    return self.jinja2.render_template(filename, **template_args)
  
  def RenderJSON(self, data):
    """Render an object as JSON to the response output stream."""
    
    self.response.headers['Content-Type'] = 'application/json'
    json.dump(data, self.response.out, indent=True, encoding="utf-8")
    
  def SetAttachment(self, file_name):
    self.response.headers['Content-Disposition'] = 'attachment;filename=%s' % file_name
    
  def SetTextMode(self):
    self.response.headers['Content-Type'] = 'text/plain'

  @staticmethod
  def ConvertToASCII(text):
    return unicodedata.normalize('NFKD', text).encode("ascii", "ignore")
  
  @classmethod
  def ISAMarkup(cls, value):
    """Jinja filter for converting IS Academia markup to HTML."""
    
    value = value.replace("&amp;", "&")
    value = value.replace("&nbsp;", " ")
    
    tags = re.findall(r"\[[^\[]*?\]", value)
    
    for tag in tags:
      if len(tag) > 7: # Empirical classification of legitimate square parentheses
        continue
      if tag in cls._isa_replacement_map:
        value = value.replace(tag, cls._isa_replacement_map[tag])
      else:
        value = value.replace(tag, "")
        
    
    return " ".join([x.strip() for x in value.split('\n')]).strip()
