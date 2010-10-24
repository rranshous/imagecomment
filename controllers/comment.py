import cherrypy
class Comment:
    @cherrypy.expose
    def index(self):
        """ returns page w/ all comments for media associated media """
        return 'comment'

    @cherrypy.expose
    def update(self):
        """ updates the comment or rating, only allow media owner or
            comment owner """
        return 'update'

    @cherrypy.expose
    def delete(self):
        """ deletes comment, only allows owner of media or owner of
            comment to delete  """
        return 'delete'

