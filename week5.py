#/opt/google_appengine/dev_appserver.py ~/workspace/Udacity/src
#/opt/google_appengine/appcfg.py update ~/workspace/Udacity/src

from ascii_chan_map import ASCII
from blog import Blog, NewPost, UniquePost, EditPost, EditRedirect, DeletePost
from login import SignUp, Login, Welcome, Logout
from jsonParse import JsonUniquePost, JsonBlog

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(homeHTML)

webPages = [('/', MainPage), 
            ('/ascii', ASCII),
            ('/blog/post/(.+).json', JsonUniquePost), 
            ('/blog/.json', JsonBlog), 
            ('/blog', Blog),
            ('/blog/', Blog), #duplicate
            ('/blog/newpost', NewPost),
            ('/blog/post/(.+)', UniquePost), 
            ('/blog/edit/([0-9]+)', EditPost), 
            ('/blog/delete/([0-9]+)', DeletePost), 
            ('/blog/edit/(.+)', EditRedirect), 
            ('/blog/signup', SignUp),
            ('/blog/login', Login),
            ('/blog/logout', Logout),
            ('/blog/welcome', Welcome)]
 
noLinks = ['/', 
           '/blog/', 
           '/blog/welcome', 
           '/blog/newpost', 
           '/blog.json', 
           '/blog/post/(.+).json', 
           '/blog/edit/(.+)', 
           '/blog/post/(.+)'] #links to hide from homepage

urls = ''
for page in webPages:
    if page[0] not in noLinks:
        name = str(page[1])
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