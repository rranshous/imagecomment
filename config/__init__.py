import os

config = {
    'here': os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
}

print 'config:%s' % config
