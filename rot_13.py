import webapp2
import cgi
let = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split()

def rot_13(string):
    rot_s = ''
    for s in string:
        if s.isalpha():
            pos = let.index(s.lower())
            if pos + 13 >= 26:
                pos -= 26
            if s.isupper():
                rot_s += let[pos + 13].upper() 
            else:
                rot_s += let[pos + 13]
        else:
            rot_s += s
    return rot_s

def escape_html(s):
    return cgi.escape(s, quote = True)

rotForm = '''
    <form method="post">
      <textarea name="text"
                style="height: 100px; width: 400px;">%(text)s</textarea>
      <br>
      <input type="submit">
    </form>
'''

rotBody = '''
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Rot 13</title>
  </head>

  <body>
    <h2>Enter some text to ROT13:</h2>
    %(form)s
  </body>

</html>
''' % {'form': rotForm}

class Rot13(webapp2.RequestHandler):
    def write_body(self, text=''):
        self.response.out.write(rotBody % {'text': text})
        
    def get(self):
        self.write_body()

    def post(self):
        user_text = self.request.get('text')
        escaped_text = escape_html(rot_13(user_text))
        self.write_body(escaped_text)