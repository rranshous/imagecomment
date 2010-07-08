from ConfigParser import ConfigParser
import fnmatch
import os
from mako.template import Template
from functools import partial
from types import MethodType
import json

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
    matches = []
    for root, dirnames, filenames in os.walk(root):
        matches += _recursive_find(filenames,patterns)
    return [os.path.join(root,m) for m in matches]

def _recursive_find(filenames,patterns):
    m = []
    for p in patterns:
        m += [x for x in fnmatch.filter(filenames,p)]
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


def get_renderer(name):
    root = config.get('template_root')
    path = os.path.join(root,'%s.mako' % name)
    template = Template(filename=path)
    # we are going to decorate the templates
    # render method to make the config available
    _r = partial(template.render,config=config)
    return _r
