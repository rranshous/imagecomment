import cherrypy
import models as m
from helpers import render, add_flash, redirect
import exceptions as e

class Album:

    @cherrypy.expose
    def index(self):
        albums = m.Album.query.order_by(m.Album.created_at.desc()).all()
        return render('/albums/index.html',albums=albums)

    @cherrypy.expose
    def default(self,*args,**kwargs):
        # TODO: support multiple albums @ a time
        albums = []

        for arg in args:
            # we'll assume it's an id for now
            found = m.Album.get(arg)
            if found:
                albums.append(found)

        if not albums:
            add_flash('error','album not found!')

        return render('/albums/single.html',album=albums[0])
