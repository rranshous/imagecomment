#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()
import pyexiv2
import json
from utils import config

form = cgi.FieldStorage()

# get the comment
comment = form.getvalue('comment')

if not comment:
    raise ValidationError('Must provide comment to add')

# get the image id
# we are going to use the json map to 
# retreive the path to the image
media_id = form.getvalue('mid')

# lookup the media path
lookup_path = config.get('map_path')
resource_map = json.load(open(lookup_path,'r'))

path = resource_map.get(media_id)
if not path:
    raise ValidationError('Media not found')

# open the meta data for the image
meta = pyexiv2.ImageMetadata(path)
meta.read()

# update the comment.
# we are going to put double new lines in between
# new single comments
COMMENT_TAG = 'Exif.Image.ImageDescription'
if COMMENT_TAG in meta.exif_keys:
    value = meta[COMMENT_TAG].value
else:
    value = ""

meta[COMMENT_TAG] = '%s\n\n%s' % (value,comment)

# write the updated file out
meta.write()

print 'Content-Type: text/html\n\n'
print 'it is done:',meta[COMMENT_TAG].value
