import webapp2
import urllib
import jinja2
import os
import string
import re
import datetime
from jinjahandler import Handler
from google.appengine.ext import db

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

def titleToUrl(title):
    "converts a title (punctuated text string) to a dash seperated url w/o stop words"
    PUNC = set(string.punctuation) #punctuation chars
    STOPWORDS = 'a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your'.split(',')
    title = re.sub('<[^<]+?>', '', title) #strip out any html in the title
    title = ''.join(let for let in title if let not in PUNC).lower().split() #list of words w/o punc and lowercased
    return '-'.join([word for word in title if word not in STOPWORDS]) #checks word isn't a stop word then joins with a dash

class BlogPost(db.Model):
    #author
    #tags
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)
    url = db.StringProperty(required = True)

class NewPost(Handler):
    "creates a new blog post, ensures no duplicate urls"
    def get(self):
        template = jinja_environment.get_template('blog_create.html')
        self.response.out.write(template.render({'blogTitle': 'CS 253 Blog', 
                                                 'subject': '', 
                                                 'content': '', 
                                                 'created': '', 
                                                 'errorSubject': '', 
                                                 'errorContent': ''}))
    '''
    def get(self):
        vals = {'blogTitle': 'CS 253 Blog', 
                'newPost': 'newPost', 
                'subject': '', 
                'content': '', 
                'created': '', 
                'errorSubject': '', 
                'errorContent': ''}
        self.render('blog_home.html', vals)
    '''

    
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            titleUrl = titleToUrl(subject)
            if titleUrl.isdigit():
                titleUrl += '-a'

            dbTitle = list(db.GqlQuery('SELECT * FROM BlogPost '
                                  'WHERE url = :1', titleUrl))
            if len(dbTitle) > 0:
                if dbTitle[0].title == titleUrl: #doesn't catch double duplicate names
                    titleUrl += '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')

            bp = BlogPost(title = subject, body = content, url = titleUrl)
            #bp = BlogPost(title = subject, body = str(dbTitle[0]), url = titleUrl)
            bp.put()
            
            self.redirect('/blog/post/%s' % titleUrl)
        else:
            if not subject:
                errorSubject = ' - Please add a subject'
            else:
                errorSubject = ''
            if not content:
                errorContent = ' - Please add some content'
            else:
                errorContent = ''
            
            template = jinja_environment.get_template('blog_create.html')
            self.response.out.write(template.render({'blogTitle': 'CS 253 Blog',
                                                     'subject': subject,
                                                     'content': content,
                                                     'errorSubject': errorSubject, 
                                                     'errorContent': errorContent}))

class Blog(webapp2.RequestHandler):
    #add multi pages (eg. 10 per page)
    def get(self):
        template_values = {'blogTitle': 'CS 253 Blog',
                           'blogDB': list(db.GqlQuery('SELECT * FROM BlogPost '
                                                      'ORDER BY created DESC '
                                                      'LIMIT 10')),
                           'cookie': self.request.cookies.get('username', '')}
        template = jinja_environment.get_template('blog_home.html')
        self.response.out.write(template.render(template_values))

class UniquePost(webapp2.RequestHandler):
    def get(self, resource):
        urlTitle = urllib.unquote(resource)
        postDB = list(db.GqlQuery('SELECT * FROM BlogPost '
                            'WHERE url = :1', urlTitle))
        if len(postDB) < 1:
            self.response.out.write("sorry that post does not exist")
        else:
            subject = postDB[0].title
            content = postDB[0].body
            created = postDB[0].created
            cookie = self.request.cookies.get('username', '')
    
            template_values = {'blogTitle': 'CS 253 Blog',
                               'subject': subject,
                               'content': content,
                               'created': created,
                               'cookie': cookie}
    
            template = jinja_environment.get_template('blog_post.html')
            self.response.out.write(template.render(template_values))
class EditPost(webapp2.RequestHandler):
    def get(self, resource):
        
        urlKey = urllib.unquote(resource)
        postKey = BlogPost.get_by_id(int(urlKey))
        
        if not postKey:
            self.response.out.write("sorry that post does not exist")
        
        subject = postKey.title
        content = postKey.body
        date = postKey.created
        url = postKey.url
        
        template = jinja_environment.get_template('blog_edit.html')
        self.response.out.write(template.render({'blogTitle': 'CS 253 Blog',
                                                 'subject': subject,
                                                 'content': content,
                                                 'created': date,
                                                 'url': url,
                                                 'errorSubject': '',
                                                 'errorContent': '',
                                                 'errorDate': '',
                                                 'errorURL': '', 
                                                 'postKey': urlKey}))

    
    def post(self, resource):
        self.response.out.write('test post')
        subject = self.request.get('subject')
        content = self.request.get('content')
        date = self.request.get('date')
        url = self.request.get('url')
        
        if subject and content and date and url:
            urlTitle = urllib.unquote(resource)
            postKey = BlogPost.get_by_id(int(urlTitle))
             
            postKey.title = subject
            postKey.body = content
            postKey.created = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
            postKey.url = url
            
            postKey.put()
            
            self.redirect('/blog/post/%s' % url)
        else:
            if not subject:
                errorSubject = ' - Please add a subject'
            else:
                errorSubject = ''
            if not content:
                errorContent = ' - Please add some content'
            else:
                errorContent = ''
            
            template = jinja_environment.get_template('blog_edit.html')
            self.response.out.write(template.render({'blogTitle': 'CS 253 Blog',
                                                     'subject': subject,
                                                     'content': content,
                                                     'errorSubject': errorSubject, 
                                                     'errorContent': errorContent}))

class EditRedirect(webapp2.RequestHandler):
    def get(self, resource):
        url = urllib.unquote(resource)
        postDB = list(db.GqlQuery('SELECT * FROM BlogPost '
                            'WHERE url = :1', url))
        
        if len(postDB) < 1:
            self.response.out.write("sorry that post does not exist")
        
        postKey = postDB[0].key().id()
        self.redirect('/blog/edit/%s' %postKey)

class DeletePost(webapp2.RequestHandler):
    def get(self, resource):
        urlKey = urllib.unquote(resource)

        template = jinja_environment.get_template('blog_delete.html')
        self.response.out.write(template.render({'blogTitle': 'CS 253 Blog',
                                                 'postKey': urlKey}))
    
    def post(self, resource):
        deleteConfirm = self.request.get('delete')

        urlKey = urllib.unquote(resource)
        postKey = BlogPost.get_by_id(int(urlKey))
        
        if deleteConfirm == urlKey:
            postKey.delete()
            self.response.out.write('Post was deleted')
        else:
            template = jinja_environment.get_template('blog_delete.html')
            self.response.out.write(template.render({'blogTitle': 'CS 253 Blog',
                                                     'postKey': urlKey}))