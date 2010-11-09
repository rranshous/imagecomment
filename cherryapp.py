#!/usr/bin/python
import cherrypy
from auth import set_user
import logging as log
import models as m
import controllers as c


if __name__ == "__main__":
    # setup the db connection
    m.setup()

    # create our app from root
    app = cherrypy.Application(c.Root())

    # setup a tool to rset our db session
    cherrypy.tools.reset_db = cherrypy.Tool('on_end_resource',
                                            m.reset_session)
    # and for setting our user
    cherrypy.tools.set_user = cherrypy.Tool('before_handler', set_user)

    # get this thing hosted
    cherrypy.quickstart(app, config='cherryconfig.ini')

