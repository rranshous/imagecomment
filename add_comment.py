#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()
import pyexiv2
import json
from utils import config, set_image_comment, get_media_page_url

form = cgi.FieldStorage()

# get the comment
comment = form.getvalue('comment')
rating = form.getvalue('rating')

# we make sure that rating is a num between 0-100
try:
    float(rating)
except TypeError:
    rating = None

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

set_image_comment(path,body=comment,rating=rating)

# where do we point them back to? that medias page
page_url = get_media_page_url(media_id)

print 'Location: %s\n\n' % page_url
