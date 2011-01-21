import cherrypy
import models as m
from helpers import render, add_flash, redirect
import lib.exceptions as e

class Public:

    @cherrypy.expose
    def index(self):
        return rener('/public/index.html')

    @cherrypy.expose
    def default(self, key):
        album = m.Album.get_by(public_key=key)
        return render('/albums/single.html',album=album)

