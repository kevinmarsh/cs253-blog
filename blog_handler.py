from blog import Blog, NewPost, UniquePost, EditPost, EditRedirect, DeletePost, FlushCache
from login import SignUp, Login, Welcome, Logout
from jsonParse import JsonUniquePost, JsonBlog

import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.redirect('/blog')

webPages = [('/', MainPage), 
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
            ('/blog/flush', FlushCache),
            ('/blog/welcome', Welcome)]

app = webapp2.WSGIApplication(webPages, debug=True)