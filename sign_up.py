import webapp2
import re


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
    return EMAIL_RE.match(email)

class SignUp(webapp2.RequestHandler):
    def write_body(self, 
                   username='', 
                   error_username='', 
                   password='',
                   error_password='', 
                   verify='', 
                   error_verify='', 
                   email='', 
                   error_email = ''):
        self.response.out.write(signUpBody % {'username': username, 
                                              'error_username': error_username, 
                                              'error_password': error_password, 
                                              'error_verify': error_verify, 
                                              'email': email,
                                              'error_email': error_email})

    def get(self):
        self.write_body()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')

        if not valid_username(user_username) or not valid_password(user_password) or user_password != user_verify or not valid_email(user_email):
            if not valid_username(user_username) or not user_username:
                error_username = 'That\'s not a valid username.'
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
            self.redirect('/confirm?username=%s' %user_username)

class SignUpConfirm(webapp2.RequestHandler):     
    def get(self):
        username = self.request.get('username')
        self.response.out.write('Welcome, %s!' %username)