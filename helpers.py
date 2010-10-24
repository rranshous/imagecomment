from utils import get_map

class PageLookup():
    """
    returns the html for a web page
    """
    def __init__(self,template_lookup=None,
                      media_lookup=None,
                      lookup_cache=None):
        self.template_lookup = templatelookup or TemplateLookup()
        self.lookup_cache = lookup_cache or {}
        self.media_lookup = media_lookup or {}

    def get(self,uri,data):
        # did we already render this ?
        if uri in self.lookup_cache:
            return self.lookup_cache.get(uri)

        # guess not
        else:
            # lets get that template
            template = self.template_lookup.get(uri)

            if not template:
                raise PageNotFound('Template not found: %s' % uri)

            # boosh
            # add our own bit of data
            data.update({'get_media_page_url':get_media_page_url,
                         'get_media_url':get_media_url})
            rendered = template.render(**data)

            # add it to our cache
            self.lookup_cache[(uri,data)] = rendered
            return rendered


class TemplateLookup():
    """
    returns the template object
    """
    def __init__(self,lookup_directory=None,cache_dir='/tmp',tmp_size=500):
        self.lookup = MakoTemplateLookup(lookup_directory,
                                         module_directory=cache_dir,
                                         collection_size=tmp_size)

    def get(self,uri,default=None):
        # this way i don't have to add the mako extention to the name
        if not '.' in uri:
            uri = '%s.mako' % uri
        try:
            return self.lookup.get_template(uri)
        except:
            return default

class MediaLookup():
    """
    returns media information based on id
    """
    def __init__(self,lookup_cache=None,media_map=None):
        self.lookup_cache = lookup_cache or {}
        self.media_map = media_map or {}
        self.updated_at = datetime.now() if lookup_cache else None

    def get(self,id,default={}):
        if id in self.lookup_cache:
            return self.lookup_cache.get(id)

        else:
            # if not we haven't read in the map yet, lets
            self.conditional_update()

            # we want to read in from the media map
            if id not in self.media_map:
                return default

            else:
                # now we need to actually compile our datas
                # simple at first
                return Media.get_dict(id)

    def iterkeys(self):
        for k in self.media_map.iterkeys():
            yield k

    def keys(self):
        # return back all the media ids
        self.conditional_update()
        return self.media_map.keys()

    def conditional_update(self):
        if not self.updated_at:
            self.update_map()
            return True
        return False

    def update_map(self):
        # we want to get the newest map on the market
        try:
            self.media_map = get_map()
        except:
            raise
            return False
        return True

class Media():
    @classmethod
    def get_dict(cls,id):
        # right now all we have is the image comment
        data = {}
        try:
            data['comments'] = utils.get_image_comments()
        except:
            pass
        return data


class TemplateNotFound(Exception):
    pass

class PageNotFound(Exception):
    pass

class MediaNotFound(Exception):
    pass
