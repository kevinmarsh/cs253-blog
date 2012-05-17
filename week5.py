#/opt/google_appengine/dev_appserver.py ~/workspace/Udacity/src
#/opt/google_appengine/appcfg.py update ~/workspace/Udacity/src

from ascii_chan_map import ASCII
from blog import Blog, NewPost, UniquePost
from login import SignUp, Login, Welcome, Logout
import cgi
import webapp2

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(homeHTML)
        
class JSON(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("hello json")

webPages = [('/', MainPage), 
            ('/ascii', ASCII),
            ('/blog', Blog),
            ('/blog/newpost', NewPost),
            ('/blog/post/([0-9]+)', UniquePost), 
            ('/signup', SignUp),
            ('/login', Login),
            ('/logout', Logout),
            ('/welcome', Welcome),
            ('/blog/post/([0-9]+)(.json)$', JSON), 
            ('/blog.json', JSON)]
 
noLinks = ['/', '/welcome', '/blog/newpost', '/blog/post/([0-9]+)']

urls = ''
for page in webPages:
    if page[0] not in noLinks:
    #    continue
    #else:
        name = escape_html(str(page[1]))
        urls += '<li><a href="%(path)s">%(name)s</a></li>\n' % {'path': page[0], 
                                                                'name': name[name.index('.') + 1 : name.find('&gt;') - 1]}

homeHTML = '''
<!DOCTYPE html>

<html>
  <head>
    <title>Kevin Marsh - Google App Engine</title>
  </head>

  <body>
    <h2>Here are the available pages for week 4:</h2>
    <ol>
        %(urls)s
    </ol>
  </body>

</html>
''' % {'urls': urls}

app = webapp2.WSGIApplication(webPages, debug=True)