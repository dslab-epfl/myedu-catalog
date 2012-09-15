#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 EPFL. All rights reserved.

"""Common request handler functionality (authentication, user info, etc.)"""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"


import json
import logging
import re
import unicodedata
import webapp2

from lxml import etree
from lxml import html

from webapp2_extras import jinja2
from webapp2_extras import sessions


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
  
  # TODO(bucur): Make this a global configuration parameter
  default_language = "en"
  
  def dispatch(self):
    self.session_store = sessions.get_store(request=self.request)
    
    try:
      webapp2.RequestHandler.dispatch(self)
    finally:
      self.session_store.save_sessions(self.response)
  
  @webapp2.cached_property
  def jinja2(self):
    """The Jinja object."""
    
    return jinja2.get_jinja2(app=self.app)
  
  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()
  
  @classmethod
  def language_prefix(cls, handler_method):
    """Decorator that adds language support to a handler."""

    def language_handler(self, lang, *args, **kwargs):
      if lang not in ["en", "fr"]:
        self.abort(404)
      
      if self.language != lang:
        self.session["language"] = lang
        
      handler_method(self, *args, **kwargs)

    return language_handler
  
  @property
  def language(self):
    return self.session.get("language", self.default_language)
  
  def GetLanguageURLFor(self, _name, language=None, *args, **kwargs):
    language = language or self.language
    if language == "__switch__":
      language = "en" if self.language != "en" else "fr"
    
    return self.uri_for(_name, lang=language, *args, **kwargs)
  
  def RenderTemplate(self, filename, template_args):
    """Render a template to the response output stream."""
    
    values = {
      "language": self.language,
      "url_for_lang": self.GetLanguageURLFor,
    }
    values.update(template_args)
    
    self.response.write(self.jinja2.render_template(filename, **values))
    
  def GetRenderedTemplate(self, filename, template_args):
    """Return a rendered template, without writing in the response."""
    
    return self.jinja2.render_template(filename, **template_args)
  
  def RenderJSON(self, data):
    """Render an object as JSON to the response output stream."""
    
    self.response.headers['Content-Type'] = 'application/json'
    json.dump(data, self.response.out, indent=True, encoding="utf-8")
    
  def SetAttachment(self, file_name):
    """Configure the response to be a file attachment."""
    
    self.response.headers['Content-Disposition'] = 'attachment;filename=%s' % file_name
    
  def SetTextMode(self):
    """Set the response content type to plain text."""
    
    self.response.headers['Content-Type'] = 'text/plain'
    
  def EncodedQuery(self, encoding="utf-8", **kwargs):
    """Encode the URL query of the request."""
    
    result = dict([(k.encode(encoding), v.encode(encoding))
                   for k, v in self.request.GET.items()])
    result.update(kwargs)
    return result

  @staticmethod
  def ConvertToASCII(text):
    """Strip accents from Unicode text."""
    
    return unicodedata.normalize('NFKD', text).encode("ascii", "ignore")
  
  @classmethod
  def ISAMarkup(cls, value, cleanup=False):
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
        
    
    value = " ".join([x.strip() for x in value.split('\n')]).strip()
    
    if cleanup:
      try:
        html_doc = html.fromstring(value)
        value = html.tostring(html_doc)
      except etree.XMLSyntaxError:
        logging.warning("Very broken HTML encountered in ISA markup.")
    
    return value
