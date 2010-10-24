#!/usr/bin/python

# we are going to generate out some flat files
# from the image map to submit to the script

import os.path
import os
from utils import read_map, config, get_renderer
from helpers import MediaLookup, TemplateLookup, PageLookup
from helpers import PageNotFound, MediaNotFound, TemplateNotFound

class PageWriter():
    """
    can write index pages, media pages
    """
    def __init__(self,file_map=None,
                      render_lookup=None,
                      template_lookup=None,
                      template_root=None,
                      pages_root=None,
                      media_dir_template='%(id)s'):
        self.pages_root = pages_root
        self.media_dir_template = media_dir_template
        self.media_lookup = media_lookup or MediaLookup()
        # the template lookup is going to be no good w/o a lookup dir
        self.template_lookup = template_lookup
        if not self.template_lookup:
            self.template_lookup = TemplateLookup(template_root)
        self.page_lookup = page_lookup or PageLookup(self.template_lookup,
                                                     self.media_lookup)

    def write_media_pages(self,ids=None):
        # if we didn't get an id than we re-write them all
        if ids is None:
            ids = self.media_lookup.keys()

        # we want to handle a list of ids
        if type(id) in (int,float,string):
            ids = [ids]

        for id in ids:
            media_dir = self.media_dir_template % ({'id':id})
            pages_dir = os.path.join(self.pages_root,id)
            index_path = os.pathjoin(pages_dir,'index.html')
            media_data = self.media_lookup.get(id)
            self.write_template('media_page',index_path,media_data)

        return True

    def write_template(self,template_name,out_path,data={}):
        with open(out_path,'w') as fh:
            try:
                fh.write(self.page_lookup.get(template_name,data))
            except PageNotFound:
                raise
            except MediaNotFound:
                raise
            except TemplateNotFound:
                raise


# get our file map
file_map = read_map(config.get('map_path'))

# we are going to go through the files
# in ID order, generating one giant flat
# file which has a form submit for each
# of the pictures.

# we also want to output a single page view
# for each media

render_lookup = {}

submit_template = get_renderer('comment_submit')
image_template = get_renderer('large_image')
image_comments = get_renderer('image_comments')
BREAK = '<hr>'

keys = sorted((int(x) for x in file_map.keys()))[:10]
keys = [str(x) for x in keys]
for id in keys:
    out = []
    out.append(BREAK)
    out.append(image_template(id=id))
    out.append(image_comments(id=id))
    out.append(submit_template(id=id))
    render_lookup[id] = '\n'.join(out)

# output our flat file
out_path = config.get('index_path')
out = '\n'.join([render_lookup.get(x) for x in keys])
with open(out_path,'w') as fh:
    fh.write(out)

# now output each of the flat files
root = config.get('pages_root')
for id in keys:
    media_dir = os.path.join(root,id)
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    index_path = os.path.join(media_dir,'index.html')
    with file(index_path,'w') as fh:
        fh.write(render_lookup.get(id))
