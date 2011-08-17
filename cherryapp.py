#!/usr/bin/python
import cherrypy
from auth import set_user, check_active_login
from helpers import set_section
import logging as log
import models as m
import controllers as c

def setup():
    # setup the db connection
    m.setup()

    # create our app from root
    app = cherrypy.Application(c.Root(), config='./cherryconfig.ini')

    # read the s3 creds off the drive
    with open('./s3_creds.txt') as fh:
        lines = fh.readlines()
        key = lines[0].strip()
        secret = lines[1].strip()
    cherrypy.config.update({ 's3_key': key, 's3_secret': secret,
                             's3_bucket_name': 'ranshousweddingphotos' })

    # setup a tool to rset our db session
    cherrypy.tools.reset_db = cherrypy.Tool('on_end_resource',
                                            m.reset_session)

    # validates a user is logged in
    cherrypy.tools.check_active_login = cherrypy.Tool('before_handler',
                                                      check_active_login,
                                                      priority = 10)

    # setting our user from session data
    cherrypy.tools.set_user = cherrypy.Tool('before_handler', set_user)

    # set values on the request object for what section / subsection
    cherrypy.tools.set_section = cherrypy.Tool('before_handler', set_section)

    return app


if __name__ == "__main__":
    app = setup()

    # get this thing hosted
    cherrypy.quickstart(app)
