#/opt/google_appengine/dev_appserver.py ~/workspace/Udacity/src
#/opt/google_appengine/appcfg.py update ~/workspace/Udacity/src

from ascii_chan import *
from blog import *
import cgi
import re

def escape_html(s):
    return cgi.escape(s, quote = True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(homeHTML)

webPages = [('/', MainPage), 
            ('/art/ascii', ASCII),
            ('/blog', Blog),
            ('/blog/newpost', NewPost),
            ('/blog/post/([0-9]+)', UniquePost)]

noLinks = ['/', '/blog/newpost', '/blog/post/([0-9]+)']

urls = ''
for page in webPages:
    if page[0] in noLinks:
        continue
    else:
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
    <h2>Here are the available pages for week 3:</h2>
    <ol>
        %(urls)s
    </ol>
  </body>

</html>
''' % {'urls': urls}

app = webapp2.WSGIApplication(webPages, debug=True)