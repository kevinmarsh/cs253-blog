import webapp2
from main_page import urls

homeHTML = '''
<!DOCTYPE html>

<html>
  <head>
    <title>Kevin Marsh - Google App Engine</title>
  </head>

  <body>
    <h2>Here are the available pages for week 2:</h2>
    <ol>
        %(urls)s
        <li><a href="datecheck">Check a valid date</a></li>
        <li><a href="rot13">Run a ROT 13</a></li>
        <li><a href="signup">Create User</a></li>
    </ol>
  </body>

</html>
''' % {'urls': urls}

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'html'
        self.response.out.write(homeHTML)