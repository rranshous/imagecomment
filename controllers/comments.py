import cherrypy
import models as m
from helpers import render, add_flash, redirect
import exceptions as e


class Comment:
    @cherrypy.expose
    def index(self):
        """ returns page w/ all comments for media associated media """
        return 'comment'

    @cherrypy.expose
    def create(self,content=None,title=None,rating=None,media_id=None,
                    tags=[], action=None):
        """ create a new comment """
        try:
            if action:
                media = m.Media.get(media_id)
                # must have something
                if not content and not title and not rating:
                    add_flash('error',
                              'Must have @ least a comment / title or rating')

                # rating must be between 1 and 5
                elif rating and not rating.isdigit() or 0> int(rating) >5:
                    add_flash('error','invalid rating!')

                # make sure our media is good
                elif media_id and not media:
                    add_flash('error',"Sry, I can't find the media!")

                else:
                    # create our new comment
                    comment = m.Comment(title=title,
                                        rating=rating,
                                        content=content,
                                        media=media,
                                        user=cherrypy.request.user)

                    # add our tags
                    for tag in tags:
                        comment.add_tag_by_name(tag)

                    # add the comment to the db
                    m.session.add(comment)
                    m.session.commit()

                    # let the user know it worked
                    add_flash('info','Comment successfully added!')

                    # send them to the page for the media they
                    # commented on
                    if media:
                        redirect('/media/%s' % media.id)
                    else:
                        redirect('/comment/%s' % comment.id)

        except Exception, ex:
            raise
            # woops, let the user know we had an error
            add_flash('error','%s' % ex)

        return render('/comments/create.html')

    @cherrypy.expose
    def update(self,id=None,content=None,title=None,rating=None,
                    media_id=None,tags=[], action=None):
        """ updates the comment or rating
            only allow comment owner """
        return 'update'

    @cherrypy.expose
    def delete(self):
        """ deletes comment, only allows owner of media or owner of
            comment to delete  """
        return 'delete'

    @cherrypy.expose
    def default(self,id):
        """ shows the media the comment is on, and the comment itself """
        pass # no one will want to permi-comment initially
