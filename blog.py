import webapp2
import urllib
import jinja2
import os
import string
import re
import datetime
import logging
from jinjahandler import Handler
from google.appengine.ext import db
from google.appengine.api import memcache

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
    "GAE db entity for blog posts"
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
        self.render('blog_create.html', 
                    subject='', 
                    content='', 
                    created='', 
                    errorSubject='', 
                    errorContent='')
    
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            titleUrl = titleToUrl(subject)
            if titleUrl.isdigit():
                titleUrl += '-num' #to prevent urls that are only numbers, breaks the edit redirect

            dbTitle = list(db.GqlQuery('SELECT * FROM BlogPost '
                                       'WHERE url = :1', titleUrl)) #use list to only hit the db once
            if len(dbTitle) > 0:
                if dbTitle[0].title == titleUrl: #prevents duplicate urls by adding date to end of url
                    titleUrl += '-' + datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')

            bp = BlogPost(title = subject, body = content, url = titleUrl)
            bp.put() #commit the blog post to the db
            recent_posts(True) #reset the cache
            self.redirect('/blog/post/%s' % titleUrl)
        else:
            errorSubject = ' - Please add a subject' if not subject else ''
            errorContent = ' - Please add some content' if not content else ''
            
            self.render('blog_create.html', 
                        subject=subject,
                        content=content,
                        errorSubject=errorSubject, 
                        errorContent=errorContent)

def recent_posts(update = False):
    key = 'recent'
    posts = memcache.get(key)
    if update or posts is None:
        logging.error("db query")
        posts = list(db.GqlQuery("SELECT * "
                                 "FROM BlogPost "
                                 "ORDER BY created DESC "
                                 "LIMIT 10"))
        memcache.set(key, [posts, datetime.datetime.now()])
    return posts

def post_cache(slug, update = False):
    key = slug
    post = memcache.get(key)
    if update or post is None:
        logging.error("db query")
        post = list(db.GqlQuery("SELECT * "
                                "FROM BlogPost "
                                "WHERE url = :1", slug))
        post = [post[0], datetime.datetime.now()]
        memcache.set(key, post)
    return post

class Blog(Handler):
    #add multi pages (eg. 10 per page)
    def get(self):
        blogPosts = recent_posts()
        query = datetime.datetime.now() - blogPosts[1]
        self.render('blog_home.html', 
                    cookie=self.request.cookies.get('username', ''), 
                    blogPosts=blogPosts[0], 
                    query=query.seconds)

class UniquePost(Handler):
    def get(self, resource):
        urlTitle = urllib.unquote(resource)
        postDB = post_cache(urlTitle)

        if postDB[0]: #if valid url
            query = datetime.datetime.now() - postDB[1]
            self.render('blog_post.html', 
                        subject=postDB[0].title, 
                        content=postDB[0].body, 
                        created=postDB[0].created, 
                        cookie=self.request.cookies.get('username', ''), 
                        query=query.seconds)
        else:
            self.write("sorry that post does not exist")

class EditPost(Handler):
    def get(self, resource):
        
        urlKey = urllib.unquote(resource)
        postKey = BlogPost.get_by_id(int(urlKey))
        
        if postKey:
            self.render('blog_edit.html', 
                        subject=postKey.title,
                        content=postKey.body,
                        created=postKey.created,
                        url=postKey.url, 
                        postKey=urlKey)
        else:
            self.response.out.write("sorry that post does not exist")

    
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
            post_cache(url, True)
            self.redirect('/blog/post/%s' % url)
        else:
            errorSubject = ' - Please add a subject' if not subject else ''
            errorContent = ' - Please add some content' if not content else ''
            
            self.render('blog_edit.html',
                        subject=subject,
                        content=content, 
                        errorSubject=errorSubject,  
                        errorContent=errorContent)

class EditRedirect(webapp2.RequestHandler):
    def get(self, resource):
        url = urllib.unquote(resource)
        postDB = list(db.GqlQuery('SELECT * FROM BlogPost '
                            'WHERE url = :1', url))
        
        if len(postDB) < 1:
            self.response.out.write("sorry that post does not exist")
        
        postKey = postDB[0].key().id()
        self.redirect('/blog/edit/%s' %postKey)

class DeletePost(Handler):
    def get(self, resource):
        urlKey = urllib.unquote(resource)
        self.render('blog_delete.html',
                    postKey=urlKey)
    
    def post(self, resource):
        deleteConfirm = self.request.get('delete')

        urlKey = urllib.unquote(resource)
        postKey = BlogPost.get_by_id(int(urlKey))
        
        if deleteConfirm == urlKey:
            postKey.delete()
            self.response.out.write('Post was deleted')
        else:
            self.render('blog_delete.html',
                        postKey=urlKey)
            
class FlushCache(Handler):
    def get(self):
        recent_posts(True)
        self.redirect('/blog')