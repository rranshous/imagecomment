import cherrypy
import models as m
from helpers import render, add_flash, redirect
from helpers import owner_or_error, error
import lib.exceptions as e
import os
from sqlalchemy import or_
from auth import public, logout_user, login_user
import mimetypes
mimetypes.init()

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

                # validate our form info
                file_data = m.Media.validate_form_data(title,file_data,comment,rating,
                                                       tags,album_id,album_name)

                for fd in file_data:
                    # create our new media
                    media = m.Media(title=title)

                    # add our new media to the session
                    m.session.add(media)

                    # who uploaded this?
                    media.user = cherrypy.request.user

                    # set the extension as the type
                    media.type = str(fd.type)

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

                    m.session.commit()

                # let our user know it worked
                add_flash('info','New media successfully created!')

                # if it's a multi upload than we don't want to redirect
                if multi:
                    return '1'

                # send them to the new media's page
                if album_name:
                    redirect('/album/%s' % album.id)
                else:
                    redirect('/media/%s' % media.id)

        except e.ValidationException, ex:
            # woops, alert of error
            add_flash('error','%s' % ex)

        if multi:
            return render('/media/create_multi.html')

        return render('/media/create.html')

    @cherrypy.expose
    def update(self,id,action=None,**kwargs):
        """ replace the (meta)data for this media, only allowed by
            media owner """
        try:

            # grab the media
            media = m.Media.get(id)

            # must have media to update media
            if not media:
                raise e.ValidationException('Media not found')

            # media must belong to user
            owner_or_error(media)

            if action:

                # we need to validate our form data
                file_data = m.Media.validate_form_data(ignore_file=True,**kwargs)
                if file_data:
                    file_data = file_data[0]

                # now we update our object

                # who uploaded this?
                media.user = cherrypy.request.user

                # set the extension as the type
                if file_data and file_data.file is not None:

                    # grab the file data
                    data = file_data.file.read()

                    if len(data) >= 0:

                        # they uploaded a new photo save it down
                        media.set_data(data)

                        media.type = str(file_data.type)

                        # add the filename
                        if file_data.filename:
                            ext = file_data.filename.rsplit('.',1)[-1]
                            if ext:
                                media.extension = ext


                # is there a comment for the photo?
                comment = kwargs.get('comment')
                rating = kwargs.get('rating')
                if comment:

                    # see if the author originally left a comment
                    if media.comments and media.comments[0].user == cherrypy.request.user:
                        c = media.comments[0]

                        # if so did something change?
                        if c.content != comment:
                            c.content = comment
                        if c.rating != rating:
                            c.rating = rating

                    else:
                        # add a new comment
                        c = m.Comment(media=media,
                                      content=comment,
                                      rating=rating,
                                      user=cherrypy.request.user)
                        m.session.add(c)


                # add our tags
                tags = kwargs.get('tags',[])
                media.set_tags(tags)

                # the album can either be an id or a
                # new name
                album_id = kwargs.get('album_id')
                album_name = kwargs.get('album_name')
                if album_id or album_name:
                    if album_id:
                        album = m.Album.get(album_id)
                    else:
                        album = m.Album.get_by(name=album_name)
                        if not album:
                            # tell our user
                            add_flash('info','New Album created: %s' % album.name)

                            album = m.Album(name=album_name,
                                            owner=cherrypy.request.user)
                            m.session.add(album)
                    media.albums.append(album)

                # add our media to the db, commit
                m.session.add(media)
                m.session.commit()

                # let our user know it worked
                add_flash('info','Media updated!')

                # send them to the media's page
                redirect('/media/%s' % media.id)

        except e.ValidationException, ex:
            add_flash('error','%s' % ex)

        return render('media/edit.html',media=media)


    @cherrypy.expose
    def delete(self,media_id=[],action=None,confirmed=False):
        """ delete this media, only allowed by media owner """
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
            # error!
            add_flash('error','%s' % ex)

        return render('/media/delete.html',media=found)


    @cherrypy.expose
    @public
    def data(self,id,filename=None,size=None):
        """ returns the data for the media, only if your authed
            to view the media """
        cherrypy.log('getting media data: %s' % id)
        try:
            media = m.Media.get(id)
            if not media:
                raise cherrypy.HTTPError(404)
            if not filename:
                filename = media.get_safe_title()
            if size:
                data = media.create_thumbnail(size)
                m.session.commit()
            else:
                data = media.get_data()

            if not data:
                error(404)

            ext = media.extension.lower() if media.extension else None
            content_type = mimetypes.types_map.get(ext,None)
            cherrypy.response.headers['Content-Type'] = content_type or 'image/jpg'

            return data
        except Exception:
            raise
            error(404)

    @cherrypy.expose
    def default(self,id):
        """ return page for media w/ given id """
        try:
            media = m.Media.get(id)
            if not media:
                raise e.ValidationException('Media not found')

            next = None
            prev = None

            album_ids = cherrypy.session.get('current_albums',None)

            # grab the next and previous media if browing an album
            if album_ids:
                next = m.Media.query.join('albums') \
                                    .filter(m.Album.id.in_(album_ids)) \
                                    .filter(m.Media.id > media.id) \
                                    .order_by(m.Media.id.asc()).first()

                prev = m.Media.query.join('albums') \
                                     .filter(m.Album.id.in_(album_ids)) \
                                     .filter(m.Media.id < media.id) \
                                     .order_by(m.Media.id.desc()).first()

        except e.ValidationException, ex:
            add_flash('error','%s' % ex)

        cherrypy.log('media: %s' % media)

        return render('/media/single.html',media=media,next=next,prev=prev)


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
                    add_flash('error','media appears to be awol!')
        except ValidationException, ex:
            add_flash('error','%s' % ex)

        return render('/media/search.html',media=media,
                        search=','.join(args))
