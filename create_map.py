#!/usr/bin/python

import json
from utils import config, recursive_find
import os.path

# we are going to go through the root
# media dir recursively
# and laying down a map w/ id's and the
# media they are associated to
root = config.get('media_root')
map_path = config.get('map_path')
media_extensions = config.get('media_extensions')
media = recursive_find(media_extensions)

# load up the existing map
# we want keys to remain constant
lookup = json.load(open(map_path,'r'))
reverse_lookup = dict((v,k) for k,v in lookup.iteritems())
lookup = {}
last_id = sorted(lookup.keys())[-1]
id = last_id + 1
for root,filename in media:
    path = os.path.join(root,filename)
    if path not in reverse_lookup:
        # we need to add it to the map
        lookup[id] = path
        id += 1

# now that we've updated the map we need to write it 
# back out
json.write(open(map_path,'w'),lookup)
