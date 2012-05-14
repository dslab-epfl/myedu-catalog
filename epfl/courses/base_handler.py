#!/usr/bin/env python

"""Common request handler functionality (authentication, user info, etc.)"""

__author__ = "stefan.bucur@epfl.ch (Stefan Bucur)"

import json
import logging
import webapp2

from google.appengine.api import urlfetch

from webapp2_extras import sessions

class BaseCourseDescriptionHandler(webapp2.RequestHandler):
  tequilla_key_url = r"http://pocketcampus.epfl.ch/tequila_auth/tequila_proxy.php?app_name=MyEdu&app_url=http://myedu.pocketcampus.org/update"
  tequilla_data_url = r"http://pocketcampus.epfl.ch/tequila_auth/tequila_proxy.php?key=%s"
  
  def dispatch(self):
    self.session_store = sessions.get_store(request=self.request)
    
    try:
      webapp2.RequestHandler.dispatch(self)
    finally:
      self.session_store.save_sessions(self.response)
      
  @webapp2.cached_property
  def session(self):
    return self.session_store.get_session()
  
  @classmethod
  def _GetTequillaKey(cls):
    result = urlfetch.fetch(cls.tequilla_key_url)
    data = json.loads(result.content)
    return data
  
  @classmethod
  def _GetTequillaData(cls, key):
    result = urlfetch.fetch(cls.tequilla_data_url % key)
    if result.status_code != 200:
      return None
    data = json.loads(result.content)
    return data
  
  def _ParseTequillaNameField(self, field):
    return field.split(",", 1)[0].strip()
  
  @webapp2.cached_property
  def user_name(self):
    if not self.session.get('tequilla_attributes'):
      return None
    
    first_name = self.session['tequilla_attributes']['firstname']
    last_name = self.session['tequilla_attributes']['name']
    
    return " ".join([self._ParseTequillaNameField(first_name),
                     self._ParseTequillaNameField(last_name)])
    
  @classmethod
  def authenticated(cls, handler_method):
    def auth_required(self, *args, **kwargs):
      if self.Authenticate():
        handler_method(self, *args, **kwargs)
      else:
        self.RedirectTequilla()
    return auth_required
  
  def RedirectTequilla(self):
    self.redirect(str(self.session['tequilla_redirect']))
  
  def Authenticate(self):
    if self.session.get('tequilla_attributes'):
      return True
    
    if self.session.get('tequilla_key'):
      # Obtain authentication info
      auth_data = self._GetTequillaData(self.session['tequilla_key'])
      if not auth_data or auth_data["status"] != 200:
        self.session.pop('tequilla_key')
        return False
      
      self.session['tequilla_attributes'] = auth_data["attributes"]
      logging.info("User authenticated: %s" % self.user_name)
      
      self.session.pop('tequilla_key')
      return True
    
    # Produce the authentication redirect
    auth_coord = self._GetTequillaKey()
    self.session['tequilla_key'] = str(auth_coord["key"])
    self.session['tequilla_redirect'] = str(auth_coord["redirect"])
    return False
