import cherrypy
from auth import setup_auth
import logging as log
#from auth import AuthController, require, member_of, name_is
import models as m
import controllers as c


class Root:
    """ sits @ The root of the app """
    media = c.Media()
    tag = c.Tag()
    comment = c.Comment()
    default = c.Media() # other than the above options it's media

    @cherrypy.expose
    def index(self):
        """ login if not authed else the home page """
        return 'index'



if __name__ == "__main__":
    # setup the db connection
    m.setup()
    # create our app from root
    app = cherrypy.Application(Root())
    # get this thing hosted
    cherrypy.quickstart(app, config='cherryconfig.ini')

