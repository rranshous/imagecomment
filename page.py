#!/usr/bin/python

# we are going to generate out some flat files
# from the image map to submit to the script


from utils import read_map, config, get_renderer

# get our file map
file_map = read_map(config.get('map_path'))

# we are going to go through the files
# in ID order, generating one giant flat
# file which has a form submit for each
# of the pictures.

submit_template = get_renderer('comment_submit')
image_template = get_renderer('large_image')
image_comments = get_renderer('image_comments')
BREAK = '<hr>'

out = []
keys = sorted((int(x) for x in file_map.keys()))
keys = [str(x) for x in keys]
for id in keys:
    out.append(BREAK)
    out.append(image_template(id=id))
    out.append(image_comments(id=id))
    out.append(submit_template(id=id))

out_path = config.get('index_path')
with open(out_path,'w') as fh:
    fh.write('\n'.join(out))
