#import urllib
#from google.appengine.ext import db
#import webapp2
#import jinja2
#import os
import hmac
from jinjahandler import Handler


SECRET = 'imsosecret'

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

class Counter(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits', 0)
        
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)
        
        visits += 1
        
        new_cookie_val = make_secure_val(str(visits))
        
        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)
        if visits > 100:
            self.write('Congrats!')
        else:
            self.write('You\'ve been here %s times!' % visits)

'''    
class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPost(webapp2.RequestHandler):
    def get(self):
        template_values = {'blogTitle': 'CS 253 Blog',
                           'newPost': 'newPost', 
                           'subject': '',
                           'content': '',
                           'created': '',
                           'errorSubject': '',
                           'errorContent': '',
                           'blogDB': db.GqlQuery('SELECT * FROM BlogPost ORDER BY created DESC')}

        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))

    
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            bp = BlogPost(title = subject, body = content)
            bp.put()
            blogId = bp.key().id()
            
            self.redirect('/blog/post/%s' % blogId)
        else:
            if not subject:
                errorSubject = ' - Please add a subject'
            else:
                errorSubject = ''
            if not content:
                errorContent = ' - Please add some content'
            else:
                errorContent = ''
            
            template_values = {'blogTitle': 'CS 253 Blog',
                               'newPost': 'newPost', 
                               'subject': subject,
                               'content': content,
                               'errorSubject': errorSubject, 
                               'errorContent': errorContent}
            
            template = jinja_environment.get_template('blog_home.html')
            self.response.out.write(template.render(template_values))

class Blog(webapp2.RequestHandler):
    def get(self):
        template_values = {'blogTitle': 'CS 253 Blog',
                           'homepage': 'homepage', 
                           'blogDB': db.GqlQuery('SELECT * FROM BlogPost ORDER BY created DESC')}

        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))

class UniquePost(webapp2.RequestHandler):
    def get(self, resource):
        postId = int(urllib.unquote(resource))
        entry = BlogPost.get_by_id(postId, parent=None)
        subject = entry.title
        content = entry.body
        created = entry.created

        template_values = {'blogTitle': 'CS 253 Blog',
                           'blogPost': 'blogPost', 
                           'subject': subject,
                           'content': content,
                           'created': created}

        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))

'''