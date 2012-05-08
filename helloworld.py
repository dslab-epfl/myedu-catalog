import cgi
import webapp2

search_page = """
<html>
  <body>
    <form action="/search" method="post">
      <div>Course Name: <textarea name="content" cols="60"></textarea></div>
      <div><input type="submit" value="Search"/></div>
    </form>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(search_page)

class ResultsPage(webapp2.RequestHandler):
  def post(self):
    self.response.out.write(
      '<html><body>Looking for %s...</body></html>' % cgi.escape(self.request.get('content')))

app = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/search', ResultsPage)], debug=True)
