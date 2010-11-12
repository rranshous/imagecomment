import cherrypy
import models as m
from helpers import render, add_flash, redirect
import lib.exceptions as e

class Tag:
    # for the index we want to return a Media who has
    # been passed our tag as a constraint

    @cherrypy.expose
    def index(self):
        """ home page! """
        return render('/tags/index.html')

    @cherrypy.expose
    def create(self,**kwargs):
        """ creates a new tag """
        return 'create'

    @cherrypy.expose
    def update(self,**kwargs):
        """ updates the tag """
        return 'update'

    @cherrypy.expose
    def delete(self,**kwargs):
        """ deletes tag, not contents """
        return 'delete'

