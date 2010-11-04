from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import os

here = os.path.abspath(os.path.dirname(__file__))
lookup = TemplateLookup(directories=[here],format_exceptions=True)

def render(path,**kwargs):
    global errors, warnings, info, lookup
    template = lookup.get_template(path)
    cherrypy.log('request: %s' % cherrypy.request)
    kwargs.update({'session':cherrypy.session,
                   'request':cherrypy.request})
    s = template.render(**kwargs)
    return s

