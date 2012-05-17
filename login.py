import re
import webapp2
from hashing import make_pw_hash, valid_pw, make_secure_val, check_secure_val
from jinjahandler import Handler
from google.appengine.ext import db

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.TextProperty(required = True)
    email = db.StringProperty()

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)
def valid_password(password):
    return PASSWORD_RE.match(password)
def valid_verify(password, verify):
    return password == verify
def valid_email(email):
    if email == '':
        return True
    return EMAIL_RE.match(email)

class SignUp(Handler):
    def write_body(self, 
                   username='', 
                   error_username='', 
                   password='',
                   error_password='', 
                   verify='', 
                   error_verify='', 
                   email='', 
                   error_email = ''):

        self.render('sign_up.html', 
                    username=username, 
                    error_username=error_username, 
                    error_password=error_password, 
                    error_verify=error_verify, 
                    email=email, 
                    error_email=error_email)
        
    def get(self):
        if self.request.cookies.get('username', '') != '':
            self.redirect('/welcome')
        self.write_body()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        error_username = ''
        
        dubName = db.GqlQuery('SELECT * FROM User WHERE username = :1', user_username)
        for entity in dubName:
            if user_username == entity.username:
                error_username = 'That name\'s already been taken.'

        if error_username != '' or not valid_username(user_username) or not valid_password(user_password) or user_password != user_verify or not valid_email(user_email):
            if not valid_username(user_username) or not user_username:
                error_username = 'That\'s not a valid username.'
            elif error_username == 'That name\'s already been taken.':
                error_username = 'That name\'s already been taken.'
            else:
                error_username = ''
            if not valid_password(user_password) or not user_password:
                error_password = 'That wasn\'t a valid password.'
            else:
                error_password = ''
            if user_password != user_verify and error_password == '':
                error_verify = 'Your passwords didn\'t match.'
            else:
                error_verify = ''
            if not user_email or valid_email(user_email):
                error_email = ''
            else:
                error_email = 'That\'s not a valid email.'
            
            self.write_body(user_username, 
                            error_username, 
                            '', 
                            error_password,
                            '',
                            error_verify, 
                            user_email, 
                            error_email)
        else:
            user_db = User(username = user_username, password = make_pw_hash(user_username, user_password), email = user_email)
            user_db.put()
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % make_secure_val(str(user_username)))
            self.redirect('/welcome')

class Login(Handler):
    def write_body(self, 
               error=''):

        self.render('sign_in.html', 
                    error=error)
    def get(self):
        if self.request.cookies.get('username', '') != '':
            self.redirect('/welcome')
        self.write_body()
    
    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        if self.request.cookies.get('username', '') != '':
            self.redirect('/welcome')
        
        userDB = db.GqlQuery('SELECT * FROM User WHERE username = :1', user_username)
        
        validLogin = False
        for a in userDB:
            if valid_pw(a.username, user_password, a.password):
                validLogin = True

        if not validLogin:
            error = 'Invalid Login'
            self.write_body(error)
        else:
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % make_secure_val(str(user_username)))
            self.redirect('/welcome')
            
class Welcome(webapp2.RequestHandler):
    def get(self):
        if self.request.cookies.get('username', '') == '':
            self.redirect('/signup')
        username = check_secure_val(str(self.request.cookies.get('username')))
        self.response.out.write('Welcome, %s!' %username)
        
class Logout(webapp2.RequestHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/; expires="Fri, 31-Dec-1954 23:59:59 GMT"')
        self.redirect('/signup')