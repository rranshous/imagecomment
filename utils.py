from ConfigParser import ConfigParser
import fnmatch
import os
from mako.template import Template
from functools import partial
from types import MethodType
import json
from pyexiv2 import Image
import re

# read in the config
config = ConfigParser()
config.read('development.ini')
_config = {}
# i prefer using a normal dict for lookups
for section in config.sections():
    _config[section] = {}
    for k,v in config.items(section):
        _config[section][k] = v
_config.update(config.defaults())
config = _config


# ty: http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
def recursive_find(root,patterns):
    if type(patterns) not in (tuple,list):
        patterns = [patterns]
    patterns = [re.compile(pattern) for pattern in patterns]
    matches = []
    for root, dirnames, filenames in os.walk(root):
        file_matches = _recursive_find(filenames,patterns)
        matches += [os.path.join(root,m) for m in file_matches]
    return matches

def _recursive_find(filenames,patterns):
    m = []
    for p in patterns:
        m += [x for x in filenames if p.match(x)]
    return m


def read_map(map_path):
    # we are going to read in the map as json
    try:
        lookup = json.load(open(map_path,'r'))
    except IOError: # no existing file
        lookup = {}
    except ValueError: # can't deserialize
        lookup = {}
    return lookup

def get_map():
    """ return default map as read from config """
    map_path = config.get('map_path')
    return read_map(map_path)

def get_renderer(name):
    root = config.get('template_root')
    path = os.path.join(root,'%s.mako' % name)
    template = Template(filename=path)
    # we are going to decorate the templates
    # render method to make the config available
    _r = partial(template.render,
                    config=config,
                    get_media_page_url=get_media_page_url,
                    get_media_url=get_media_url)
    return _r

IMAGE_COMMENT_TAG = 'Exif.Image.ImageDescription'
COMMENT_DELIMINATOR = '\n\n'
def get_image_comments(path):
    image = Image(path)
    image.readMetadata()
    comments = image.getComment()
    comments = comments.split(COMMENT_DELIMINATOR)
    comments = [x for x in comments if x]
    return comments

def set_image_comments(path,comments,append=False):
    if comments.__class__ in (tuple,list):
        comments = COMMENT_DELIMINATOR.join(comments)
    image = Image(path)
    image.readMetadata()
    if append:
        existing = image.getComment()
        delim = COMMENT_DELIMINATOR if existing else ''
        comments = '%s%s%s' % (existing,delim,comments)
    image.setComment(comments)
    image.writeMetadata()


def get_media_page_url(mid):
    """ return url for media's page """
    return '%s%s' % (config.get('media_pages_root'),mid)

def get_media_url(mid):
    """ returns the url for media's data """
    return '%s%s' % (config.get('media_files_root'),mid)
