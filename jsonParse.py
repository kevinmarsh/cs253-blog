import webapp2
import urllib
from google.appengine.ext import db
import json

class JsonUniquePost(webapp2.RequestHandler):
    def get(self, resource):
        self.response.headers['Content-Type'] = 'application/json'
        urlTitle = str(urllib.unquote(resource))
        
        posts = list(db.GqlQuery('SELECT * FROM BlogPost '
                            'WHERE url = :1', urlTitle))
        if len(posts) == 0: #if the URL isn't found in the db
            self.response.out.write('Sorry that post does not exist')
        else:
            output = {"content": str(posts[0].title), 
                      "created": posts[0].created.strftime('%a %B %d %H:%M:%S %Y'), 
                      "subject": str(posts[0].title)}
            jsonOutput = json.dumps(output)
            self.response.out.write(jsonOutput)

class JsonBlog(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        posts = list(db.GqlQuery('SELECT * FROM BlogPost '))
        
        jsonOutput = []
        for entry in posts: #add each db item into a list formated for json
            output = {"content": str(entry.title), 
                      "created": entry.created.strftime('%a %B %d %H:%M:%S %Y'), 
                      "subject": str(entry.title)}
            jsonOutput.append(output)
        self.response.out.write(json.dumps(jsonOutput))