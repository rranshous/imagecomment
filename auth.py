from elixir import metadata
import models as m
import cherrypy
from helpers import error, redirect
from decorator import decorator
from cherrypy import HTTPError

def get_user_passwords():
    users = m.User.query.all()
    # later we can return dict which lookups from model
    data = dict(((u.handle,u.password) for u in users))
    return data

def hash_password(p):
    return m.User.create_password_hash(p)

def set_user():
    """ checks that a user is logged in or raises 403,
        if user is logged in sets the cherrypy.request.user """
    cherrypy.request.user = get_user_from_session()
    return True

def get_user_from_session():
    """ returns user found from session info """
    return m.User.get_by(handle=cherrypy.session.get('user_handle'))

def get_user():
    return get_user_from_session()

def check_active_login():
    """
    checks that there is an active user or sends back a 403
    """

    # make sure there is a handle
    if not cherrypy.session.get('user_handle'):
        error(403)

    # make sure there's a hash in the session
    if not cherrypy.session.get('user_hash'):
        error(403)

    # find the user and check the hash against his password
    user = m.User.get_by(handle=cherrypy.session.get('user_handle'))
    if not user:
        error(403)
    if hash_password(user.password) != cherrypy.session.get('user_hash'):
        error(403)

    return user

def auth_credentials(handle,password):
    """ returns user object if password is good """
    user = m.User.get_by(handle=handle)
    if not user or hash_password(password) != user.password:
        return False
    return user

def login_user(user):
    """ updates the session from the user object """
    cherrypy.session['user_hash'] = hash_password(user.password)
    cherrypy.session['user_handle'] = user.handle

def logout_user():
    cherrypy.lib.sessions.expire()

@decorator
def public(f,*args,**kwargs):
    f._cp_config = {'cherrypy.tools.check_active_login.on':False}
    return f(*args,**kwargs)

def public_redirect(new_url):
    """ if the user isn't logged in pushes to another url """
    def _public_redirect(f):
        def __public_redirect(*args,**kwargs):
            # check the login
            try:
                check_active_login()
            except HTTPError:
                redirect(new_url)

            return f(*args,**kwargs)
        return __public_redirect
    return _public_redirect
