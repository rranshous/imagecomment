#!/usr/bin/python

import json
from utils import config, recursive_find
import os.path

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
media = recursive_find(root,media_extensions.split(','))

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
        lookup[id] = path
        id += 1

# now that we've updated the map we need to write it 
# back out
json.dump(lookup,open(map_path,'w'))
