import webapp2
import cgi

from google.appengine.ext import db

def escape_html(s):
    return cgi.escape(s, quote = True)

html = '''
<!DOCTYPE html>

<html>
    <head>
        <title>Kevin Marsh - Google App Engine</title>
    </head>
    <style>
        body {
            font-family: sans-serif;
            width: 800px;
            margin: 0 auto;
            padding: 10px;
        }
        .error { color: red; }
        label {
            display: block;
            font-size: 20px;
        }
        input[type=text] {
            width: 400px;
            font-size: 20px;
            padding: 2px;
        }
        textarea {
            width: 400px;
            height: 200px;
            font-size: 17px;
            font-family: monospace;
        }
        input[type=submit] {
            font-size: 24px;
        }
        hr { margin-top: 20px auto; }
        .art + .art { margin-top: 20px; }
        .art-title {
            font-weight: bold;
            font-size: 20px;
        }
        .art-body {
            margin: 0;
            font-size: 17px;
        }
    </style>

    <body>
        <h2>ASCII chan</h2>
        <form method="post">
            <label>
                <div class="art-title">title</div>
                <input type="text" name="title" value="%(title)s">
            </label>
            <label>
                <div class="art-body">art</div>
                <textarea name="art">%(art)s</textarea>
            </label>
            
            <div class="error">%(error)s</div>
            
            <input type="submit">
        </form>
        
        <hr>
        
        %(arts)s
        
    </body>

</html>
'''

        
def art_loop(arts):
    output = ''
    for art in arts:
        output += '''
        <div class="art">
            <div class="art-title">%(art.title)s</div>
            <pre class="art-body">%(art.art)s</pre>
        </div>
        ''' % {'art.title': art.title, 'art.art': art.art}
    return output

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class ASCII(webapp2.RequestHandler):
    
    def write_form(self, 
                   title='',
                   art='',
                   error='',
                   arts=''):
        artDB = db.GqlQuery('SELECT * FROM Art ORDER BY created DESC')
        arts = art_loop(artDB)
        
        self.response.out.write(html % {'title': title, 'art': art, 'error': error, 'arts': arts})
    
    def get(self):
        self.write_form()
    
    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        
        if title and art:
            a = Art(title = title, art = art)
            a.put()
            
            self.redirect('/art/ascii')
        else:
            error = 'we need both a title and some artwork'
            self.write_form(title, art, error)