import cherrypy
from media import Media
from tag import Tag
from user import User
from comment import Comment
from helpers import render

class Root:
    """ sits @ The root of the app """
    media = Media()
    tag = Tag()
    tags = tag
    user = User()
    users = user
    comment = Comment()
    default = Media() # other than the above options it's media

    @cherrypy.expose
    def index(self):
        """ login if not authed else the home page """
        return render('/index.html')

