import cherrypy
from auth import setup_auth
import logging as log
from models import setup,Media,Tag,Comment

class Root:
    """ sits @ The root of the app """
    media = Media()
    tag = Tag()
    comment = Comment()
    default = Media() # other than the above options it's media

    @cherrypy.expose
    def index(self):
        """ login if not authed else the home page """
        return 'index'



if __name__ == "__main__":
    setup()
    app = cherrypy.Application(Root())
    app.wsgiapp.pipeline.append(('repoze.who', setup_auth))
    cherrypy.quickstart(app, config='cherryconfig.ini')

