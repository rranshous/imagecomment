import cherrypy
class User:
    @cherrypy.expose
    def index(self):
        return 'index'

    @cherrypy.expose
    def create(self,**kwargs):
        return 'create'

    @cherrypy.expose
    def update(self,handle=None,email=None,password1=None,
                    password2=None,action=None):
        """ users can only edit themselves """
        user = cherrypy.request.user
        try:
            if action:
                if handle:
                    user.handle = handle
                if email:
                    user.email_address = email
                if password1:
                    if password1 != password2:
                        raise e.ValidationException('Passwords do not match')
                    user.password = password1
                redirect('/user/%s' % user.id)
        except Exception, ex:
            raise
            add_flash('error','%s' % ex)

    @cherrypy.expose
    def delete(self,**kwargs):
        return 'delete'

