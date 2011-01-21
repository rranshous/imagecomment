import cherrypy
import models as m
from helpers import render, add_flash, redirect
import lib.exceptions as e
import os
from sqlalchemy import or_

class Media:
    @cherrypy.expose
    def index(self,search=None):
        """ returns page w/ media embedded + comments """

        frontpage_media = m.Media.query. \
                                    order_by(m.Media.created_at.desc()). \
                                    limit(10).all()

        return render('/media/index.html',frontpage_media=frontpage_media)

    @cherrypy.expose
    def create(self,title=None,file_data=None,comment=None,rating=None,
                    tags=[],album_id=None,album_name=None,action=None,
                    multi=False):
        """ creates new media, metadata and media data submitted """
        # check and see if they are creating new media

        try:
            if action:
                # must have a title!
                if not title:
                    raise e.ValidationException('error','title required!')

                # can't create a media entry w/o data!
                elif (isinstance(file_data,list) and not file_data) or \
                     (not isinstance(file_data,list) and
                      not file_data.filename):
                    print 'file_data:',file_data
                    raise e.ValidationException('error','must upload file!')

                # legit ratings only!
                elif rating and not rating.isdigit() or 0> int(rating) >5:
                    raise e.ValidationException('error','invalid rating!')

                # we might be getting multiple files
                if not isinstance(file_data,list):
                    file_data = [file_data]


                for fd in file_data:
                    # create our new media
                    media = m.Media(title=title)

                    # who uploaded this?
                    media.user = cherrypy.request.user
                    cherrypy.log('user: %s' % media.user)

                    # set the extension as the type
                    cherrypy.log('content type: %s' % (fd.type))
                    media.type = fd.type

                    # add the filename
                    if fd.filename:
                        ext = fd.filename.rsplit('.',1)[-1]
                        if ext:
                            media.extension = ext

                    # if there is a comment from the author add it
                    if comment:
                        c = m.Comment(media=media,
                                      content=comment,
                                      rating=rating,
                                      user=cherrypy.request.user)
                        m.session.add(c)

                    # save file data to the drive
                    media.set_data(fd.file.read())

                    # add our tags
                    for tag_name in tags:
                        media.add_tag_by_name(tag_name)

                    # the album can either be an id or a
                    # new name
                    if album_id or album_name:
                        if album_id:
                            album = m.Album.get(album_id)
                        else:
                            album = m.Album.get_by(name=album_name)
                            if not album:
                                album = m.Album(name=album_name,
                                                owner=cherrypy.request.user)
                                m.session.add(album)
                        media.albums.append(album)

                    # add our media to the db, commit
                    m.session.add(media)
                m.session.commit()

                # let our user know it worked
                add_flash('info','New media successfully created!')

                # send them to the new media's page
                if album_name:
                    redirect('/album/%s' % album.id)
                else:
                    redirect('/media/%s' % media.id)

        except Exception, ex:
            raise
            # woops, alert of error
            add_flash('error')
            m.session.rollback()

        if multi:
            return render('/media/create_multi.html')

        return render('/media/create.html')

    @cherrypy.expose
    def update(self,**kwargs):
        """ replace the (meta)data for this media, only allowed by
            media owner """
        return 'update'

    @cherrypy.expose
    def delete(self,media_id=[],action=None,confirmed=False):
        """ delete this media, only allowed by media owner """
        cherrypy.log('media_id: %s' % media_id)
        cherrypy.log('confirmed: %s' % confirmed)
        try:
            found = []
            if not media_id:
                add_flash('error','no media selected to delete')
            else:
                for id in media_id:
                    media = m.Media.get(id)
                    if not media:
                        raise e.ValidationException('Media not found')
                    found.append(media)
                    if confirmed:
                        m.session.delete(media)
                if confirmed:
                    m.session.commit()
                    add_flash('info','Media successfully deleted')
                    redirect('/media/')

        except Exception, ex:
            raise
            # error!
            add_flash('error','%s' % ex)

        return render('/media/delete.html',media=found)


    @cherrypy.expose
    def data(self,id,filename=None,size=None):
        """ returns the data for the media, only if your authed
            to view the media """
        media = m.Media.get(id)
        if not media:
            raise cherrypy.HTTPError(404)
        if not filename:
            filename = media.get_safe_title()
        cherrypy.log('media_path: %s'%media.media_path)
        if size:
            path = media.create_thumbnail(size)
        else:
            path = media.media_path
        cherrypy.log('path: %s' % path)
        if path and os.path.exists(path):
            return cherrypy.lib.static.serve_file(path,
                                                  name = filename)
        else:
            return redirect('/img/no_thumbnail.gif')

    @cherrypy.expose
    def default(self,id):
        """ return page for media w/ given id """
        try:
            media = m.Media.get(id)
            if not media:
                raise e.ValidationException('Media not found')
        except ValidationException, ex:
            add_flash('error','%s' % ex)

        cherrypy.log('media: %s' % media)


        return render('/media/single.html',media=media)


    @cherrypy.expose
    def search(self,*args,**kwargs):
        """ use the args to find media """
        media = []
        try:
            for arg in args:
                # start by checking for it by id
                found = m.Media.get(arg)

                if not found:
                    found = m.Media.query.join('user').filter_by(handle=arg). \
                                          order_by(m.Media.created_at).first()

                if not found:
                    found = m.Media.query.filter(m.Media.title==arg). \
                                          order_by(m.Media.created_at).first()

                if found:
                    media = found

                # whaaa, no media?
                if not media:
                    cherrypy.log('flashing')
                    add_flash('error','media appears to be awol!')
        except ValidationException, ex:
            add_flash('error','%s' % ex)

        return render('/media/search.html',media=media,
                        search=','.join(args))
