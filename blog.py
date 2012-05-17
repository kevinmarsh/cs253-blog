import webapp2
import urllib
import jinja2
import os
from google.appengine.ext import db

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

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
                           'blogDB': db.GqlQuery('SELECT * FROM BlogPost ORDER BY created DESC'),
                           'cookie': self.request.cookies.get('username', '')}
        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))

class UniquePost(webapp2.RequestHandler):
    def get(self, resource):
        postId = int(urllib.unquote(resource))
        entry = BlogPost.get_by_id(postId, parent=None)
        subject = entry.title
        content = entry.body
        created = entry.created
        cookie = self.request.cookies.get('username', '')

        template_values = {'blogTitle': 'CS 253 Blog',
                           'blogPost': 'blogPost', 
                           'subject': subject,
                           'content': content,
                           'created': created,
                           'cookie': cookie}

        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))