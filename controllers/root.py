import cherrypy
from media import Media
from tags import Tag
from users import User
from comments import Comment
from albums import Album
from helpers import render, redirect, add_flash
from auth import public, logout_user, login_user
import models as m

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
    @public
    def login(self,username=None,password=None,action=None,endpoint=None,
                   new_user=None):
        """ prompts the user to login, creates the user if it doesn't exist """


        # see if they are trying to login / create user
        if action or username or password:

            # if they didn't provide a password than we need to
            # either create a new user or prompt them for pass if one exists
            if not password:
                user = m.User.get_by(handle=username)
                if user:
                    return render('/login_password.html',username=username)

                else:
                    return render('/login_new_user.html',username=username)

            # if we are creating a new user, do so
            if new_user == 'true':
                user = m.User(handle=username)
                user.password = password
                m.session.commit()

            # if they gave us a username and a password then they are
            # trying to login
            if not login_user(username,password):
                # fail !
                add_flash('error','Your login has failed!')

            else:

                # yay, success. push them to their next point
                if endpoint:
                    redirect(endpoint)

                # or home
                else:
                    redirect('/')


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
