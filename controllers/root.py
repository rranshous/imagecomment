import cherrypy
from media import Media
from tags import Tag
from users import User
from comments import Comment
from albums import Album
from helpers import render, redirect

class Root:
    """ sits @ The root of the app """
    media = Media()
    tag = Tag()
    user = User()
    comment = Comment()
    album = Album()
    default = Media() # other than the above options it's media

    @cherrypy.expose
    def index(self):
        """ login if not authed else the home page """
        return render('/index.html')
    
    @cherrypy.expose
    def logout(self):
        """ clear the sesion to logout the user """
        cherrypy.lib.sessions.expire()
        redirect('/')

    @cherrypy.expose
    def contact(self):
        return render('/contact.html')
    contact_methods = contact
    contact_me = contact
