import cherrypy
from media import Media
from tags import Tag
from users import User
from comments import Comment
from albums import Album
from helpers import render, redirect
from auth import public, logout_user, public_redirect

class Root:
    """ sits @ The root of the app """
    media = Media()
    tag = Tag()
    user = User()
    comment = Comment()
    album = Album()
    default = Media() # other than the above options it's media

    @cherrypy.expose
    @public_redirect('/login')
    def index(self):
        """ login if not authed else the home page """
        return render('/index.html')

    @cherrypy.expose
    @public
    def login(self,username=None,password=None,action=None):
        """ prompts the user to login, creates the user if it doesn't exist """

        # log them out
        logout_user()

        # see if they are trying to login / create user
        if action:
            # if they gave us a username and a password then they are
            # trying to login
            pass

        return render('/login_front.html',username=username)

    @cherrypy.expose
    def logout(self):
        """ clear the sesion to logout the user """
        logout_user()
        redirect('/')

    @cherrypy.expose
    def contact(self):
        return render('/contact.html')
    contact_methods = contact
    contact_me = contact
