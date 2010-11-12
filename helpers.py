from templates import render
import cherrypy
from cherrypy import HTTPRedirect

def add_flash(msg_type,msg=None):
    if not msg:
        msg = msg_type
        msg_type = 'info'

    cherrypy.session.setdefault(msg_type,[]).append(msg)

def redirect(*args,**kwargs):
    raise HTTPRedirect(*args,**kwargs)

def set_section():
    pieces = cherrypy.request.path_info.split('/')
    cherrypy.request.section_name = pieces[1]
    cherrypy.log('section_name: %s' % pieces[1])
    if len(pieces) > 2:
        cherrypy.request.subsection_name = pieces[2]
    else:
        cherrypy.request.subsection_name = ''

def is_active_section(s):
    return cherrypy.request.section_name == s

def is_active_subsection(s):
    return cherrypy.request.subsection_name == s
