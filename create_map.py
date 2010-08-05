#!/usr/bin/python

import json
from utils import config, recursive_find
import os

# we are going to go through the root
# media dir recursively
# and laying down a map w/ id's and the
# media they are associated to
root = config.get('media_root')
assert root, 'wtf no root?'
map_path = config.get('map_path')
assert map_path, 'wtf no map path?'
media_extensions = config.get('media_extensions')
assert media_extensions, 'wtf no media extensions?'
# we need our media extensions to be regex patterns
media_extensions = ['.*%s' % x for x in media_extensions.split(',')]
media = recursive_find(root,media_extensions)

# load up the existing map
# we want keys to remain constant
try:
    lookup = json.load(open(map_path,'r'))
except IOError: # no existing file
    lookup = {}
except ValueError: # can't deserialize
    lookup = {}

reverse_lookup = dict((v,k) for k,v in lookup.iteritems())
if lookup.keys():
    last_id = sorted(lookup.keys())[-1]
else:
    last_id = 0

id = int(last_id) + 1
for path in media:
    if path not in reverse_lookup:
        # we need to add it to the map
        path = os.path.abspath(path)
        lookup[id] = path
        id += 1

# now we need to create symbolic links for all
# of the media so the webserver can access it
# on a flat dir
flat_dir = config.get('flat_media_root')

# we'll go through only placing down new links
for id,path in lookup.iteritems():
    place = os.path.join(flat_dir,str(id))
    if not os.path.exists(place):
        os.symlink(path,place)

# now that we've updated the map we need to write it 
# back out
json.dump(lookup,open(map_path,'w'))
