
import cherrypy
import memcache

## global memcache client from config
def MemcacheClient():
    cherrypy.log('setting up memcache client: %s'
                 % cherrypy.config.get('memcache_address'))
    return memcache.Client(cherrypy.config.get('memcache_address'))
