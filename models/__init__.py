from elixir import *
import datetime
import cherrypy
from hashlib import sha1
from tempfile import NamedTemporaryFile
import models as m
import os

def reset_session():
    try:
        session.rollback()
        session.expunge_all()
        session.remove()
    except:
        pass
    return

def setup():
    metadata.bind = "sqlite:///dbs/media.db"
    metadata.bind.echo = False
    setup_all()

class User(Entity):
    using_options(tablename='users')

    # users "name"
    handle = Field(Unicode(75))
    handle.public = True
    # url of their avatar
    avatar_url = Field(UnicodeText)
    avatar_url.public = True
    # hash of password
    password_hash = Field(UnicodeText)

    media = OneToMany('Media')
    comments = OneToMany('Comment')

    def set_password(self,p):
        """ sets users password hash based on passed string """
        self.password_hash = self.create_password_hash(p)

    password = property(lambda a: a.password_hash,
                        set_password)

    @classmethod
    def create_password_hash(cls,p):
        """ returns back hashed version of password """
        return sha1(p).hexdigest()


class Tag(Entity):
    using_options(tablename='tags')

    name = Field(Unicode(100))
    description = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToMany('Media')
    relates_to = ManyToMany('Tag')

    def __repr__(self):
        return '<Tag "%s">' % self.name

class Comment(Entity):
    using_options(tablename='comments')

    title = Field(Unicode(100))
    rating = Field(Integer)
    content = Field(UnicodeText)
    created_at = Field(DateTime, default=datetime.datetime.now)

    media = ManyToOne('Media')
    user = ManyToOne('User')

    def __repr__(self):
        return '<Comment "%s" "%s">' % (self.title,self.rating)

class Media(Entity):
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

    def set_data(self,data):
        # we are going to update our data file
        self.size = len(data)
        cherrypy.log('setting data: %s' % len(data))
        if not self.media_path:
            t = NamedTemporaryFile(delete=False,
                                   dir=cherrypy.config.get('media_root'),
                                   suffix='.%s'%self.extension)
            fh = t.file
            self.media_path = os.path.abspath(t.name)
        else:
            fh = file(self.media_path,'wb')
        cherrypy.log('adding_data: %s' % self.media_path)
        fh.write(data)
        fh.close()
        m.session.commit()
        return True

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

    def __repr__(self):
        return '<Media "%s" %s">' % (self.title,self.type)
