import cherrypy
class User:
    @cherrypy.expose
    def index(self):
        return 'index'

    @cherrypy.expose
    def create(self,**kwargs):
        return 'create'

    @cherrypy.expose
    def update(self,**kwargs):
        return 'update'

    @cherrypy.expose
    def delete(self,**kwargs):
        return 'delete'

