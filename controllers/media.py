import cherrypy
import models as m
from helpers import render, add_flash, redirect
import exceptions as e
import os
from sqlalchemy import or_

class Media:
    @cherrypy.expose
    def index(self,search=None):
        """ returns page w/ media embedded + comments """

        return render('/media/index.html')

    @cherrypy.expose
    def create(self,title=None,file_data=None,comment=None,rating=None,
                    tags=[]):
        """ creates new media, metadata and media data submitted """
        # check and see if they are creating new media

        try:
            if title:
                # can't create a media entry w/o data!
                if file_data is None:
                    add_flash('error','no file data')

                # legit ratings only!
                elif rating and not rating.isdigit() or 0 > int(rating) > 10:
                    add_flash('error','rating must be between 0 and 5!')

                else:
                    # create our new media
                    media = m.Media(title=title)

                    # who uploaded this?
                    media.user = cherrypy.request.user
                    cherrypy.log('user: %s' % media.user)

                    # save file data to the drive
                    media.set_data(file_data.file.read())

                    # set the extension as the type
                    media.type = file_data.type

                    # if there is a comment from the author add it
                    if comment:
                        comment = m.Comment(media=media,
                                            content=comment,
                                            rating=rating,
                                            user=cherrypy.request.user)
                        m.session.add(comment)

                    # add our tags
                    for tag_name in tags:
                        media.add_tag_by_name(tag_name)

                    # add the filename
                    if file_data.filename:
                        ext = file_data.filename.rsplit('.',1)[-1]
                        if ext:
                            media.extension = ext

                    # add our media to the db, commit
                    m.session.add(media)
                    m.session.commit()

                    # let our user know it worked
                    add_flash('info','New media successfully created!')

                    # send them to the new media's page
                    redirect('/media/%s' % media.id)

        except Exception, ex:
            raise
            # woops, alert of error
            add_flash('error','%s' % ex)


        return render('/media/create.html')

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
    def data(self,id):
        """ returns the data for the media, only if your authed
            to view the media """
        media = m.Media.get(id)
        if not media:
            raise cherrypy.HTTPError(404)
        return cherrypy.lib.static.serve_file(media.media_path,
                                              content_type=media.type,
                                              name=media.get_safe_title())

    @cherrypy.expose
    def default(self,*args,**kwargs):

        cherrypy.log('args: %s' % str(args))

        media = []
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
                media.append(found)

        cherrypy.log('media: %s' % media)

        # whaaa, no media?
        if not media:
            cherrypy.log('flashing')
            add_flash('error','media appears to be awol!')

        return render('/media/single.html',media=media)

    def check_match(self,*args,**kwargs):
        """ arg could be the id or title of a media,
            if not match and kwarg bool=True return False
            if no match, else not found """

        # check if it matches:
        if media:
            self.media
            return self.index(*args,**kwargs)

        # id
        # title
        # media type
        # username
        pass

