from elixir import *
import datetime
import cherrypy
from hashlib import sha1
from tempfile import NamedTemporaryFile
import models as m
import os
from subprocess import call

## helper functions ##
def add_tag_by_name(self,name):
    tag = Tag.get_by(name=name)
    if not tag:
        tag = Tag(name=name)
        session.add(tag)
    if tag not in self.tags:
        self.tags.append(tag)

def reset_session():
    try:
        session.rollback()
        session.expunge_all()
        session.remove()
    except:
        pass
    return

def setup():
#    metadata.bind = cherrypy.config.get('db_url')
    metadata.bind = "sqlite:///./dbs/media.db"
    metadata.bind.echo = False
    setup_all()

## end helper functions ##

# for now
BaseEntity = Entity

class User(BaseEntity):
    using_options(tablename='users')

    # users "name"
    handle = Field(Unicode(75))
    handle.public = True
    # url of their avatar
    avatar_url = Field(UnicodeText)
    avatar_url.public = True
    # hash of password
    password_hash = Field(UnicodeText)
    # email address
    email_address = Field(Unicode(120))

    # admin bool flag
    is_admin = Field(BOOLEAN(False))

    media = OneToMany('Media')
    comments = OneToMany('Comment')
    albums = OneToMany('Album')

    def set_password(self,p):
        """ sets users password hash based on passed string """
        self.password_hash = self.create_password_hash(p)

    password = property(lambda a: a.password_hash,
                        set_password)

    @classmethod
    def create_password_hash(cls,p):
        """ returns back hashed version of password """
        return sha1(p).hexdigest()

    def get_tags(self):
        tags = Tag.query.join('media').filter(Media.user==self).all()
        return tags


class Tag(BaseEntity):
    using_options(tablename='tags')

    name = Field(Unicode(100))
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToMany('Media')
    relates_to = ManyToMany('Tag')
    comments = ManyToMany('Comment')
    albums = ManyToMany('Album')

    def __repr__(self):
        return '<Tag "%s">' % self.name

class Album(BaseEntity):
    using_options(tablename='albums')

    name = Field(Unicode(100))
    created_at = Field(DateTime, default=datetime.datetime.now)

    comments = OneToMany('Comment')
    media = ManyToMany('Media')
    tags = ManyToMany('Tag')
    owner = ManyToOne('User')
    relates_to = ManyToMany('Album')

    add_tag_by_name = add_tag_by_name

    def __repr__(self):
        return '<Album "%s">' % self.name

class Comment(BaseEntity):
    using_options(tablename='comments')

    title = Field(Unicode(100))
    rating = Field(Integer)
    content = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToOne('Media')
    user = ManyToOne('User')
    tags = ManyToMany('Tag')
    album = ManyToOne('Album')

    add_tag_by_name = add_tag_by_name

    def __repr__(self):
        return '<Comment "%s" "%s">' % (self.title,self.rating)

class Media(BaseEntity):
    using_options(tablename='media')

    title = Field(Unicode(100))
    size = Field(Float)
    type = Field(Unicode(80))
    extension = Field(Unicode(10))
    media_path = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    comments = OneToMany('Comment')
    tags = ManyToMany('Tag')
    user = ManyToOne('User')
    albums = ManyToMany('Album')

    add_tag_by_name = add_tag_by_name

    def set_data(self,data):
        # we are going to update our data file
        self.size = len(data)
        cherrypy.log('setting data: %s' % len(data))
        if not self.media_path:
            t = NamedTemporaryFile(delete=False,
                                   dir=cherrypy.config.get('media_root'),
                                   suffix='.%s'%self.extension,
                                   prefix='media_')
            fh = t.file
            self.media_path = os.path.abspath(t.name)
        else:
            fh = file(self.media_path,'wb')
        cherrypy.log('adding_data: %s' % self.media_path)
        fh.write(data)
        fh.close()
        return True

    def create_thumbnail(self,w,h='',overwrite=False):
        """ creats a thumbnail of the image @ the given size,
            writes the thumbnail to the drive w/ size as
            the prefix """

        if self.is_image():
            w,h = map(str,(w,h))
            if not h:
                h = w
            if 'x' in w:
                size = w
            else:
                size = '%sx%s' % (w,h)
            file_name = os.path.basename(self.media_path)
            thumbnail_root = cherrypy.config.get('thumbnail_root')
            out_path = os.path.join(thumbnail_root,
                                    '%s_%s' % (size,file_name))
            if os.path.exists(out_path) and not overwrite:
                return out_path

            cmd = ['convert','-thumbnail',size,self.media_path,out_path]
            cherrypy.log('cmd: %s' % cmd)
            r = call(cmd) # TODO check return code
            cherrypy.log('out path: %s' % out_path)
            return out_path

        return None

    @classmethod
    def get_random_path(cls):
        # we are going to pick a random name off the root path
        root_path = cherrypy.config.get('media_root')
        temp_file = NamedTemporaryFile(delete=False,dir=root_path)
        return temp_file.name

    def add_tag_by_name(self,name):
        tag = Tag.get_by(name=name)
        if not tag:
            tag = Tag(name=name)
            session.add(tag)
        if tag not in self.tags:
            self.tags.append(tag)

    def get_safe_title(self):
        title = self.title or self.id
        title.replace(' ','_').replace('\n','_').strip()
        return '%s.%s' % (title,self.extension)

    def is_image(self):
        image_extensions = ('jpg','png','gif','jpeg')
        for e in image_extensions:
            if self.extension.lower() == e:
                return True
        return False

    def is_video(self):
        video_extensions = ('avi','mpeg','mpg','mp4','mov')
        for e in video_extensions:
            if self.extension.lower() == e:
                return True
        return False

    def __repr__(self):
        return '<Media "%s" %s">' % (self.title,self.type)



