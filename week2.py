from hello_world import HelloWorld
from date_check import *
from rot_13 import *
from sign_up import *

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(homeHTML)

webPages = [('/', MainPage), 
            ('/hello', HelloWorld),
            ('/datecheck', DateCheck),
            ('/thanks', ThanksHandler),
            ('/rot13', Rot13),
            ('/signup', SignUp),
            ('/confirm', SignUpConfirm)]

noLinks = ['/', '/thanks', '/confirm']

urls = ''
for page in webPages:
    if page[0] in noLinks:
        continue
    else:
        name = escape_html(str(page[1]))
        urls += '<li><a href="%(path)s">%(name)s</a></li>\n' % {'path': page[0], 'name': name[name.index('.') + 1 : name.find('&gt;') - 1]}

homeHTML = '''
<!DOCTYPE html>

<html>
  <head>
    <title>Kevin Marsh - Google App Engine</title>
  </head>

  <body>
    <h2>Here are the available pages for week 2:</h2>
    <ol>
        %(urls)s
    </ol>
  </body>

</html>
''' % {'urls': urls}

app = webapp2.WSGIApplication(webPages, debug=True)