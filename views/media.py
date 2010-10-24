class Media:
    @cherrypy.expose
    def index(self):
        """ returns page w/ media embedded + comments """
        return "Hello world!"

    @cherrypy.expose
    def create(self,**kwargs):
        """ creates new media, metadata and media data submitted """
        return 'create'

    @cherrypy.expose
    def update(self,**kwargs):
        """ replace the (meta)data for this media, only allowed by
            media owner """
        return 'update'

    @cherrypy.expose
    def delete(self):
        """ delete this media, only allowed by media owner """
        return 'delete'

    @cherrypy.expose
    def data(self):
        """ returns the data for the media, only if your authed
            to view the media """
        return 'data'

    @cherrypy.expose
    def default(self,*args,**kwargs):
        """ we want to be able to find the media based on args.
            args could be title of media, id of media, or less
            specific such as type or owner """

        # check if it matches:

        # id
        # title
        # media type
        # username
        pass

