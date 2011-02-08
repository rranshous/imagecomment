import cherrypy
import models as m
from helpers import render, add_flash, redirect
import lib.exceptions as e

class Album:

    @cherrypy.expose
    def index(self):
        albums = m.Album.query.order_by(m.Album.created_at.desc()).all()
        return render('/albums/index.html',albums=albums)

    @cherrypy.expose
    def edit(self,album_id=None,album_name=None,public=None,action=None):
        try:
            if action:
                # we must have an album id
                if not album_id:
                    raise e.ValidationException('error','album required')

                # grab our album
                album = m.Album.get(album_id)
                if not album:
                    raise e.ValidationException('error','album not found')

                # if they passed us an album_name set it
                if album_name is not None:
                    album.name = album_name

                # public?
                if public is not None:
                    album.set_public(public)

                # save our changes
                m.session.commit()

                # let them know it went well
                add_flash('info','Album info updated')

                # send them to the album's page
                redirect('/album/%s' % album.id)

            elif album_id:
                album = m.Album.get(album_id)
                return render('albums/edit.html',album=album)

        except Exception, ex:
            raise
            add_flash('error')
            m.session.rollback()

        # if you don't supply an album Id we'll list them all
        albums = m.Album.query.all()
        return render('/albums/edit_list.html',albums=albums)


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
