
import cherrypy
import memcache

## global memcache client from config
cherrypy.log('setting up memcache client: %s'
             % cherrypy.config.get('memcache_address'))
memcache_client = memcache.Client(cherrypy.config.get('memcache_address'))
