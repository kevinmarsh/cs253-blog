import os
import urllib2
from xml.dom import minidom

import webapp2
import jinja2
 
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
    #ip = "4.2.2.2" #this overrides the ip for development purposes
    url = IP_URL + ip #combie ip with the hostip.info url
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except URLError:
        return
    
    if content:
        d = minidom.parseString(content)
        coords = d.getElementsByTagName("gml:coordinates")
        if coords and coords[0].firstChild.nodeValue:
            lon, lat = str(coords[0].firstChild.nodeValue).split(',')
            return db.GeoPt(lat, lon)
        return

GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false"
def gmaps_img(points):
    url = GMAPS_URL
    for p in points:
        url += '&markers=%(lat)s,%(lon)s'% {'lat': str(p.lat), 'lon': str(p.lon)}
    return url

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    coords = db.GeoPtProperty()

class Handler(webapp2.RequestHandler):
    def write(self, *a,**kw):
        self.response.out.write(*a,**kw)
        
    def render_str(self,template,**params):
        t=jinja_env.get_template(template)
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))


class ASCII(Handler):
    def render_front(self,title="",art="",error=""):
        arts = db.GqlQuery("SELECT * "
                           "FROM Art "
                           "ORDER BY created DESC "
                           "LIMIT 10")
        arts = list(arts) #this creates a copy of the output of the query
        
        points = [a.coords for a in arts if a.coords != None]
        
        img_url = None
        if points:
            img_url = gmaps_img(points)
        
        self.render("ascii.html",title=title,art=art,error=error,arts=arts, img_url=img_url)
    
    def get(self):
        self.render_front() #default page
    
    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        
        if title and art:
            a = Art(title = title, art = art)
            coords = get_coords(self.request.remote_addr)
            if coords: #if it has cordinates add them to the db
                a.coords = coords
            a.put() #adds to the Art DB
            self.redirect('/ascii') #reloads the page
        else:
            error = 'we need both a title and some artwork'
            self.write_form(title, art, error)