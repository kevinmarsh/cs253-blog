import webapp2

class HelloWorld(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, Udacity!')
       
app = webapp2.WSGIApplication([('/', HelloWorld)],
                              debug=True)