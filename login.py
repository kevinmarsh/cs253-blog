import re
from hashing import make_pw_hash, valid_pw, make_secure_val, check_secure_val
from jinjahandler import Handler
from google.appengine.ext import db

class User(db.Model):
    #join date
    #what blog posts have they authored
    #admin privlages
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
    if email == '': #allows blank passwords since they are not required
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
        if self.request.cookies.get('username', '') != '': #if the user is already signed in, redirect away
            self.redirect('/blog/welcome')
        self.write_body()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        error_username = ''
        
        dubName = db.GqlQuery('SELECT * FROM User WHERE username = :1', user_username)
        if user_username == dubName[0].username:
            error_username = 'That name\'s already been taken.'

        if error_username != '' or not valid_username(user_username) or not valid_password(user_password) or user_password != user_verify or not valid_email(user_email):
            if not valid_username(user_username) or not user_username:
                error_username = 'That\'s not a valid username.'
            elif error_username == 'That name\'s already been taken.':
                error_username = 'That name\'s already been taken.'
            else: error_username = ''
                
            if not valid_password(user_password) or not user_password:
                error_password = 'That wasn\'t a valid password.'
            else: error_password = ''
            
            if user_password != user_verify and error_password == '':
                error_verify = 'Your passwords didn\'t match.'
            else: error_verify = ''
            
            if not user_email or valid_email(user_email): error_email = ''
            else: error_email = 'That\'s not a valid email.'
            
            self.write_body(username=user_username, 
                            error_username=error_username, 
                            error_password=error_password,
                            error_verify=error_verify, 
                            email=user_email, 
                            error_email=error_email)
        else:
            user_db = User(username = user_username, 
                           password = make_pw_hash(user_username, user_password), 
                           email = user_email)
            user_db.put() #add user to database
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % make_secure_val(str(user_username)))
            self.redirect('/blog/welcome') #set cookie and redirect

class Login(Handler):
    "Function to login in users, checking salted passwords to username in db"
    def write_body(self, error=''):
        self.render('sign_in.html', error=error)
        
    def get(self):
        if self.request.cookies.get('username', '') != '':
            self.redirect('/blog/welcome')
        self.write_body()
    
    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        if self.request.cookies.get('username', '') != '':
            self.redirect('/blog/welcome')
        
        user = db.GqlQuery('SELECT * FROM User WHERE username = :1', user_username)
        
        if valid_pw(user[0].username, user_password, user[0].password):
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % make_secure_val(str(user_username)))
            self.redirect('/blog/welcome')
        else:
            error = 'Invalid Login'
            self.write_body(error)
            
class Welcome(Handler):
    def get(self):
        if self.request.cookies.get('username', '') == '':
            self.redirect('/signup')
        username = check_secure_val(str(self.request.cookies.get('username')))
        self.write('Welcome, %s!' %username)
        self.write('<br><a href="/">Return Home</a>')
        
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/; expires="Fri, 31-Dec-1954 23:59:59 GMT"')
        self.redirect('/blog/signup')