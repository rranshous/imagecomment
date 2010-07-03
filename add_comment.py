#!/usr/bin/python

import cgi
import cgib
cgib.enable()
import pyexiv2
import json

form = cgi.FieldStorage()

# get the comment
comment = form.getvalue('comment').value

if not comment:
    raise ValidationError('Must provide comment to add')

# get the image id
# we are going to use the json map to 
# retreive the path to the image
media_id = form.getvalue('mid')

# lookup the media path
lookup_path = config.get('lookup_path')
resource_map = json.load(open(lookup_path,'r'))

path = resource_map.get(media_id)
if not path:
    raise ValidationError('Media not found')

# open the meta data for the image
meta = pyexiv2.ImageMetaData(path)
meta.read()

# update the comment.
# we are going to put double new lines in between
# new single comments
COMMENT_TAG = 'Exif.Image.Comments'
if COMMENT_TAG in meta.exif_tags:
    file_comment = meta[COMMENT_TAG]
else:
    file_comment = ""

file_comment += "\n\n%s" % comment
meta[COMMENT_TAG] = file_comment

# write the updated file out
meta.write()
